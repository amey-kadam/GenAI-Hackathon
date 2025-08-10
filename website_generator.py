import os
import json
import tempfile
import shutil
import zipfile
from typing import Dict, Any
from schema import Spec, Page, Section
from component_templates import ComponentGenerator

class WebsiteGenerator:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.component_generator = ComponentGenerator(api_key)

    def clean_unicode(self, text: str) -> str:
        """Clean problematic Unicode characters for Windows compatibility"""
        # Replace common problematic Unicode characters with safe alternatives
        replacements = {
            '✨': '*',
            '🚀': '*',
            '🎯': '*',
            '💡': '*',
            '⚡': 'Lightning',
            '🔒': 'Security',
            '🎧': 'Support',
            '📱': 'Mobile',
            '💻': 'Desktop',
            '🌟': '*',
            '🔥': 'Hot',
            '💰': 'Money',
            '📈': 'Growth',
            '🎉': 'Party',
            '🏆': 'Trophy',
            '💎': 'Premium',
            '⭐': '*',
            '🎨': 'Art',
            '🔧': 'Tools',
            '📊': 'Analytics',
        }
        
        for unicode_char, replacement in replacements.items():
            text = text.replace(unicode_char, replacement)
        return text

    def generate_component(self, section: Section, design_tokens: Dict[str, Any]) -> str:
        """Generate React component code for a section"""
        try:
            component_code = self.component_generator.generate_component(
                section.type, 
                design_tokens, 
                section.props
            )
            
            # Ensure we have a valid string
            if component_code is None or not isinstance(component_code, str):
                print(f"Warning: generate_component returned {type(component_code)} for {section.type}, retrying...")
                # Retry with a simpler prompt
                component_code = self.component_generator.generate_simple_component(section.type, design_tokens)
            
            return self.clean_unicode(component_code)
        
        except Exception as e:
            print(f"Error generating component {section.type}: {e}")
            # Retry with a simple component generation
            try:
                return self.component_generator.generate_simple_component(section.type, design_tokens)
            except Exception as retry_error:
                print(f"Retry failed for {section.type}: {retry_error}")
                # Generate a minimal component as last resort
                return self.generate_minimal_component(section.type)

    def generate_minimal_component(self, section_type: str) -> str:
        """Generate a minimal component as absolute last resort"""
        router_import = ""
        if section_type in ["Header", "Footer"]:
            router_import = "import { Link } from 'react-router-dom';"
        
        return f"""import React from 'react';
{router_import}

export default function {section_type}() {{
  return (
    <section className="py-20 px-4 bg-background">
      <div className="max-w-4xl mx-auto text-center">
        <h2 className="text-3xl font-bold font-heading mb-8 text-foreground">
          {section_type} Section
        </h2>
        <p className="font-body text-gray-600">
          This is a {section_type.lower()} section. Content will be loaded dynamically.
        </p>
      </div>
    </section>
  );
}}"""

    def generate_page(self, page: Page, spec: Spec) -> str:
        """Generate a complete page component"""
        # Track which components we've imported
        imported_components = set()
        sections_import = []
        sections_jsx = []
        
        # Check if Header and Footer are already in the page sections
        section_types = [section.type for section in page.sections]
        has_header = "Header" in section_types
        has_footer = "Footer" in section_types
        
        # Determine page name for unique components if needed
        page_name = page.route.replace('/', '').title() or 'Home'
        
        # Add Header at the beginning - use unique component name if multiple pages
        if not has_header:
            header_component = f"{page_name}Header" if page_name != 'Home' else "Header"
            sections_import.append(f"import {header_component} from '../components/{header_component}';")
            sections_jsx.append(f"      <{header_component} />")
            imported_components.add(header_component)
        
        # Add all sections from the page
        for section in page.sections:
            component_name = section.type
            # Make section components unique to this page if not Header/Footer
            if component_name not in ['Header', 'Footer'] and page_name != 'Home':
                component_name = f"{page_name}{section.type}"
            
            if component_name not in imported_components:
                sections_import.append(f"import {component_name} from '../components/{component_name}';")
                imported_components.add(component_name)
            sections_jsx.append(f"      <{component_name} />")
        
        # Add Footer at the end - use unique component name if multiple pages
        if not has_footer:
            footer_component = f"{page_name}Footer" if page_name != 'Home' else "Footer"
            if footer_component not in imported_components:
                sections_import.append(f"import {footer_component} from '../components/{footer_component}';")
            sections_jsx.append(f"      <{footer_component} />")
        
        imports = "\n".join(sections_import)
        jsx_sections = "\n".join(sections_jsx)
        
        page_code = f"""import React from 'react';
{imports}

export default function {page_name}Page() {{
  return (
    <div className="min-h-screen">
{jsx_sections}
    </div>
  );
}}"""
        
        return page_code

    def create_missing_pages(self, spec: Spec) -> list:
        """Create pages for common navigation routes that might be missing"""
        existing_routes = {page.route for page in spec.pages}
        common_routes = ['/', '/about', '/services', '/contact']
        
        pages = list(spec.pages)  # Copy existing pages
        
        # Add missing common pages
        for route in common_routes:
            if route not in existing_routes:
                # Create a basic page structure
                sections = []
                
                if route == '/about':
                    sections = [
                        Section(type="Hero", props={"title": "About Us", "subtitle": "Learn more about our company"}),
                        Section(type="RichText", props={"content": "About content"})
                    ]
                elif route == '/services':
                    sections = [
                        Section(type="Hero", props={"title": "Our Services", "subtitle": "What we offer"}),
                        Section(type="FeatureGrid", props={"title": "Services"})
                    ]
                elif route == '/contact':
                    sections = [
                        Section(type="Hero", props={"title": "Contact Us", "subtitle": "Get in touch"}),
                        Section(type="ContactForm", props={})
                    ]
                
                new_page = Page(route=route, sections=sections)
                pages.append(new_page)
                print(f"Created missing page for route: {route}")
        
        return pages

    def generate_package_json(self, project_name: str) -> str:
        """Generate package.json"""
        return json.dumps({
            "name": project_name.lower().replace(" ", "-"),
            "private": True,
            "version": "0.0.0",
            "type": "module",
            "scripts": {
                "dev": "vite",
                "build": "vite build",
                "preview": "vite preview"
            },
            "dependencies": {
                "react": "^18.2.0",
                "react-dom": "^18.2.0",
                "react-router-dom": "^6.8.0"
            },
            "devDependencies": {
                "@types/react": "^18.2.15",
                "@types/react-dom": "^18.2.7",
                "@vitejs/plugin-react": "^4.0.3",
                "autoprefixer": "^10.4.14",
                "postcss": "^8.4.24",
                "tailwindcss": "^3.3.0",
                "vite": "^4.4.5"
            }
        }, indent=2)

    def generate_vite_config(self) -> str:
        """Generate vite.config.js"""
        return """import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
})"""

    def generate_tailwind_config(self, design_tokens: Dict[str, Any]) -> str:
        """Generate tailwind.config.js with design tokens"""
        colors = design_tokens.get('colors', {})
        fonts = design_tokens.get('font', {})
        
        return f"""/** @type {{import('tailwindcss').Config}} */
export default {{
  content: [
    "./index.html",
    "./src/**/*.{{js,ts,jsx,tsx}}",
  ],
  theme: {{
    extend: {{
      colors: {{
        primary: '{colors.get("primary", "#3B82F6")}',
        background: '{colors.get("background", "#FFFFFF")}',
        foreground: '{colors.get("foreground", "#111111")}',
      }},
      fontFamily: {{
        heading: ['{fonts.get("heading", "Inter")}', 'sans-serif'],
        body: ['{fonts.get("body", "Inter")}', 'sans-serif'],
      }},
      borderRadius: {{
        DEFAULT: '{design_tokens.get("radius", "8px")}',
      }},
    }},
  }},
  plugins: [],
}}"""

    def generate_app_component(self, pages: list) -> str:
        """Generate main App.jsx"""
        imports = ["import React from 'react';", "import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';"]
        routes = []
        
        for page in pages:
            page_name = page.route.replace('/', '').title() or 'Home'
            imports.append(f"import {page_name}Page from './pages/{page_name}Page';")
            routes.append(f'        <Route path="{page.route}" element={{<{page_name}Page />}} />')
        
        imports_str = "\n".join(imports)
        routes_str = "\n".join(routes)
        
        return f"""{imports_str}

function App() {{
  return (
    <Router>
      <Routes>
{routes_str}
      </Routes>
    </Router>
  );
}}

export default App;"""

    def generate_main_jsx(self) -> str:
        """Generate main.jsx"""
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
        """Generate index.css with Tailwind imports"""
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
        """Generate index.html"""
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
        """Generate postcss.config.js"""
        return """export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}"""

    def generate_readme(self, project_name: str) -> str:
        """Generate README.md"""
        return f"""# {project_name}

A modern website built with React, Vite, and Tailwind CSS.

## Getting Started

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

3. Open your browser and visit the URL shown in the terminal (usually http://localhost:5173)

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build

## Tech Stack

- React 18
- Vite
- Tailwind CSS
- React Router
"""

    def generate_website(self, spec: Spec) -> str:
        """Generate complete website and return path to zip file"""
        # Create missing pages for common navigation routes
        all_pages = self.create_missing_pages(spec)
        
        # Create temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = os.path.join(temp_dir, spec.project['name'].replace(' ', '-').lower())
            os.makedirs(project_dir)
            
            # Create directory structure
            src_dir = os.path.join(project_dir, 'src')
            components_dir = os.path.join(src_dir, 'components')
            pages_dir = os.path.join(src_dir, 'pages')
            
            os.makedirs(src_dir)
            os.makedirs(components_dir)
            os.makedirs(pages_dir)
            
            # Generate root files
            with open(os.path.join(project_dir, 'package.json'), 'w', encoding='utf-8') as f:
                f.write(self.generate_package_json(spec.project['name']))
            
            with open(os.path.join(project_dir, 'vite.config.js'), 'w', encoding='utf-8') as f:
                f.write(self.generate_vite_config())
            
            with open(os.path.join(project_dir, 'tailwind.config.js'), 'w', encoding='utf-8') as f:
                f.write(self.generate_tailwind_config(spec.designTokens.model_dump()))
            
            with open(os.path.join(project_dir, 'postcss.config.js'), 'w', encoding='utf-8') as f:
                f.write(self.generate_postcss_config())
            
            with open(os.path.join(project_dir, 'index.html'), 'w', encoding='utf-8') as f:
                f.write(self.generate_index_html(spec.project['name']))
            
            with open(os.path.join(project_dir, 'README.md'), 'w', encoding='utf-8') as f:
                f.write(self.generate_readme(spec.project['name']))
            
            # Generate src files
            with open(os.path.join(src_dir, 'main.jsx'), 'w', encoding='utf-8') as f:
                f.write(self.generate_main_jsx())
            
            with open(os.path.join(src_dir, 'index.css'), 'w', encoding='utf-8') as f:
                f.write(self.generate_index_css())
            
            with open(os.path.join(src_dir, 'App.jsx'), 'w', encoding='utf-8') as f:
                f.write(self.generate_app_component(all_pages))
            
            # Generate components - create unique components for each page
            generated_components = set()
            
            for page in all_pages:
                page_name = page.route.replace('/', '').title() or 'Home'
                
                # Generate unique Header and Footer for non-Home pages
                if page_name != 'Home':
                    # Generate unique Header
                    header_name = f"{page_name}Header"
                    if header_name not in generated_components:
                        # Create a dummy section for Header generation
                        header_section = Section(type="Header", props={})
                        header_code = self.generate_component(header_section, spec.designTokens.model_dump())
                        header_code = header_code.replace("export default function Header()", f"export default function {header_name}()")
                        with open(os.path.join(components_dir, f'{header_name}.jsx'), 'w', encoding='utf-8') as f:
                            f.write(header_code)
                        generated_components.add(header_name)
                    
                    # Generate unique Footer
                    footer_name = f"{page_name}Footer"
                    if footer_name not in generated_components:
                        # Create a dummy section for Footer generation
                        footer_section = Section(type="Footer", props={})
                        footer_code = self.generate_component(footer_section, spec.designTokens.model_dump())
                        footer_code = footer_code.replace("export default function Footer()", f"export default function {footer_name}()")
                        with open(os.path.join(components_dir, f'{footer_name}.jsx'), 'w', encoding='utf-8') as f:
                            f.write(footer_code)
                        generated_components.add(footer_name)
                else:
                    # Generate standard Header and Footer for Home page
                    if "Header" not in generated_components:
                        header_section = Section(type="Header", props={})
                        header_code = self.generate_component(header_section, spec.designTokens.model_dump())
                        with open(os.path.join(components_dir, 'Header.jsx'), 'w', encoding='utf-8') as f:
                            f.write(header_code)
                        generated_components.add("Header")
                    
                    if "Footer" not in generated_components:
                        footer_section = Section(type="Footer", props={})
                        footer_code = self.generate_component(footer_section, spec.designTokens.model_dump())
                        with open(os.path.join(components_dir, 'Footer.jsx'), 'w', encoding='utf-8') as f:
                            f.write(footer_code)
                        generated_components.add("Footer")
                
                # Generate page-specific section components
                for section in page.sections:
                    component_name = section.type
                    if component_name not in ['Header', 'Footer'] and page_name != 'Home':
                        component_name = f"{page_name}{section.type}"
                    
                    if component_name not in generated_components:
                        print(f"Generating component: {component_name}")
                        
                        # Generate all components using the API
                        component_code = self.generate_component(section, spec.designTokens.model_dump())
                        
                        # Ensure component_code is a string
                        if not isinstance(component_code, str):
                            print(f"Warning: Component code for {component_name} is not a string: {type(component_code)}")
                            component_code = self.generate_minimal_component(section.type)
                        
                        # Update component name in code if it's a page-specific component
                        if page_name != 'Home' and section.type not in ['Header', 'Footer']:
                            component_code = component_code.replace(f"export default function {section.type}()", f"export default function {component_name}()")
                        
                        with open(os.path.join(components_dir, f'{component_name}.jsx'), 'w', encoding='utf-8') as f:
                            f.write(component_code)
                        generated_components.add(component_name)
                        generated_components.add(section.type)
            
            # Generate pages
            for page in all_pages:
                page_name = page.route.replace('/', '').title() or 'Home'
                page_code = self.generate_page(page, spec)
                with open(os.path.join(pages_dir, f'{page_name}Page.jsx'), 'w', encoding='utf-8') as f:
                    f.write(page_code)
            
            # Create ZIP file
            zip_path = os.path.join(tempfile.gettempdir(), f"{spec.project['name'].replace(' ', '-').lower()}.zip")
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(project_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arc_name = os.path.relpath(file_path, temp_dir)
                        zipf.write(file_path, arc_name)
            
            return zip_path