"""
Robust WebsiteGenerator

This version keeps the original behavior but:
- Validates spec structure
- Converts routes into safe PascalCase component/page names
- Handles missing designTokens gracefully
- Adds clearer logging and safer string replacements
"""
from __future__ import annotations
import os
import json
import tempfile
import shutil
import zipfile
import re
from typing import Dict, Any, List

# NOTE: These imports must exist in your project. If they don't, the generator will raise an ImportError.
try:
    from schema import Spec, Page, Section
except Exception as e:
    Spec = None
    Page = None
    Section = None

try:
    from component_templates import ComponentGenerator
except Exception:
    ComponentGenerator = None

def route_to_pascal_case(route: str) -> str:
    """
    Convert route like '/about-us/team' -> 'AboutUsTeam'
    Root '/' becomes 'Home'
    """
    if not route or route == "/":
        return "Home"
    # Remove leading/trailing slashes, split on non-alphanumeric
    parts = re.split(r"[^0-9a-zA-Z]+", route.strip("/"))
    parts = [p for p in parts if p]
    return "".join(p.title() for p in parts) or "Home"

class WebsiteGenerator:
    def __init__(self, api_key: str):
        if ComponentGenerator is None:
            raise ImportError("component_templates.ComponentGenerator not available")
        self.api_key = api_key
        self.component_generator = ComponentGenerator(api_key)

    def clean_unicode(self, text: str) -> str:
        if not isinstance(text, str):
            return str(text or "")
        replacements = {
            '✨': '*', '🚀': '*', '🎯': '*', '💡': '*',
            '⚡': 'Lightning', '🔒': 'Security', '🎧': 'Support',
            '📱': 'Mobile', '💻': 'Desktop', '🌟': '*', '🔥': 'Hot',
        }
        for k, v in replacements.items():
            text = text.replace(k, v)
        return text

    def generate_component(self, section: "Section", design_tokens: Dict[str, Any]) -> str:
        try:
            component_code = self.component_generator.generate_component(
                section.type,
                design_tokens,
                getattr(section, "props", {}) or {}
            )
            if component_code is None or not isinstance(component_code, str):
                # fallback to simpler generator if available
                if hasattr(self.component_generator, "generate_simple_component"):
                    component_code = self.component_generator.generate_simple_component(section.type, design_tokens)
                else:
                    component_code = None
            if not component_code:
                return self.generate_minimal_component(section.type)
            return self.clean_unicode(component_code)
        except Exception as e:
            print(f"Error generating component '{section.type}': {e}")
            try:
                return self.component_generator.generate_simple_component(section.type, design_tokens)
            except Exception as e2:
                print(f"Retry/simple generation failed for {section.type}: {e2}")
                return self.generate_minimal_component(section.type)

    def generate_minimal_component(self, section_type: str) -> str:
        router_import = ""
        if section_type in ["Header", "Footer"]:
            router_import = "import { Link } from 'react-router-dom';"
        return f"""import React from 'react';
{router_import}

export default function {section_type}() {{
  return (
    <section className="py-12 px-4 bg-background">
      <div className="max-w-4xl mx-auto text-center">
        <h2 className="text-3xl font-bold mb-6 text-foreground">{section_type} Section</h2>
        <p className="text-sm text-gray-600">This is a placeholder for the {section_type} component.</p>
      </div>
    </section>
  );
}}"""

    def generate_page(self, page: "Page", spec: "Spec") -> str:
        imported_components = []
        jsx_parts = []
        page_name = route_to_pascal_case(getattr(page, "route", "/"))

        # ensure header/footer handling
        section_types = [getattr(s, "type", "") for s in getattr(page, "sections", [])]
        has_header = "Header" in section_types
        has_footer = "Footer" in section_types

        # add header if missing
        if not has_header:
            header_component = "Header" if page_name == "Home" else f"{page_name}Header"
            imported_components.append(f"import {header_component} from '../components/{header_component}';")
            jsx_parts.append(f"      <{header_component} />")

        # add sections
        for section in getattr(page, "sections", []):
            comp_name = getattr(section, "type", "Section")
            if comp_name not in ("Header", "Footer") and page_name != "Home":
                comp_name = f"{page_name}{comp_name}"
            imported_components.append(f"import {comp_name} from '../components/{comp_name}';")
            jsx_parts.append(f"      <{comp_name} />")

        # footer if missing
        if not has_footer:
            footer_component = "Footer" if page_name == "Home" else f"{page_name}Footer"
            if footer_component not in [imp.split()[1] for imp in (ic.split() for ic in imported_components)]:
                imported_components.append(f"import {footer_component} from '../components/{footer_component}';")
            jsx_parts.append(f"      <{footer_component} />")

        imports = "\n".join(dict.fromkeys(imported_components))  # dedupe preserving order
        jsx = "\n".join(jsx_parts)

        return f"""import React from 'react';
{imports}

export default function {page_name}Page() {{
  return (
    <div className="min-h-screen">
{jsx}
    </div>
  );
}}"""

    def create_missing_pages(self, spec: "Spec") -> List["Page"]:
        existing_routes = {getattr(p, "route", "") for p in getattr(spec, "pages", [])}
        common_routes = ['/', '/about', '/services', '/contact']
        pages = list(getattr(spec, "pages", []))

        for route in common_routes:
            if route not in existing_routes:
                sections = []
                if route == '/about':
                    sections = [Section(type="Hero", props={"title": "About Us", "subtitle": "Learn more"})]
                elif route == '/services':
                    sections = [Section(type="Hero", props={"title": "Our Services"})]
                elif route == '/contact':
                    sections = [Section(type="Hero", props={"title": "Contact"})]
                pages.append(Page(route=route, sections=sections))
                print(f"Created missing page for route: {route}")
        return pages

    def generate_package_json(self, project_name: str) -> str:
        safe_name = re.sub(r"[^a-z0-9\-]+", "-", project_name.lower()).strip("-") or "website"
        data = {
            "name": safe_name,
            "private": True,
            "version": "0.0.0",
            "type": "module",
            "scripts": {"dev": "vite", "build": "vite build", "preview": "vite preview"},
            "dependencies": {"react": "^18.2.0", "react-dom": "^18.2.0", "react-router-dom": "^6.8.0"},
            "devDependencies": {
                "@types/react": "^18.2.15",
                "@types/react-dom": "^18.2.7",
                "@vitejs/plugin-react": "^4.0.3",
                "autoprefixer": "^10.4.14",
                "postcss": "^8.4.24",
                "tailwindcss": "^3.3.0",
                "vite": "^4.4.5"
            }
        }
        return json.dumps(data, indent=2)

    def generate_vite_config(self) -> str:
        return """import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
})"""

    def generate_tailwind_config(self, design_tokens: Dict[str, Any]) -> str:
        colors = design_tokens.get('colors', {}) if isinstance(design_tokens, dict) else {}
        fonts = design_tokens.get('font', {}) if isinstance(design_tokens, dict) else {}
        primary = colors.get("primary", "#3B82F6")
        background = colors.get("background", "#FFFFFF")
        foreground = colors.get("foreground", "#111111")
        heading = fonts.get("heading", "Inter")
        body = fonts.get("body", "Inter")
        radius = design_tokens.get("radius", "8px") if isinstance(design_tokens, dict) else "8px"

        return f"""/** @type {{import('tailwindcss').Config}} */
export default {{
  content: [
    "./index.html",
    "./src/**/*.{{js,ts,jsx,tsx}}",
  ],
  theme: {{
    extend: {{
      colors: {{
        primary: '{primary}',
        background: '{background}',
        foreground: '{foreground}',
      }},
      fontFamily: {{
        heading: ['{heading}', 'sans-serif'],
        body: ['{body}', 'sans-serif'],
      }},
      borderRadius: {{
        DEFAULT: '{radius}',
      }},
    }},
  }},
  plugins: [],
}}"""

    def generate_app_component(self, pages: List["Page"]) -> str:
        imports = ["import React from 'react';", "import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';"]
        routes = []
        for page in pages:
            route = getattr(page, "route", "/")
            page_name = route_to_pascal_case(route)
            imports.append(f"import {page_name}Page from './pages/{page_name}Page';")
            routes.append(f'        <Route path="{route}" element={{<{page_name}Page />}} />')
        return "\n".join(imports) + "\n\nfunction App() {\n  return (\n    <Router>\n      <Routes>\n" + "\n".join(routes) + "\n      </Routes>\n    </Router>\n  );\n}\n\nexport default App;"

    def generate_main_jsx(self) -> str:
        return """import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)"""

    def generate_index_css(self) -> str:
        return """@tailwind base;
@tailwind components;
@tailwind utilities;

body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}"""

    def generate_index_html(self, project_name: str) -> str:
        return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{project_name}</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>"""

    def generate_postcss_config(self) -> str:
        return """export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}"""

    def generate_readme(self, project_name: str) -> str:
        return f"""# {project_name}

A modern website built with React, Vite, and Tailwind CSS.

## Getting Started

1. Install dependencies:
```bash
npm install
