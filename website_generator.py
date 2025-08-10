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
                print(f"Warning: generate_component returned {type(component_code)} for {section.type}, using fallback")
                return self.get_fallback_component(section.type)
            
            return self.clean_unicode(component_code)
        
        except Exception as e:
            print(f"Error generating component {section.type}: {e}")
            return self.get_fallback_component(section.type)

    def get_fallback_component(self, section_type: str) -> str:
        """Fallback components if generation fails"""
        fallbacks = {
            "Header": """import React, { useState } from 'react';
import { Link } from 'react-router-dom';

export default function Header() {
  const [open, setOpen] = useState(false);
  return (
    <header className="bg-background shadow sticky top-0 z-50">
      <div className="max-w-6xl mx-auto px-4 flex justify-between items-center h-16">
        <div className="text-xl font-bold text-primary">MySite</div>
        <nav className="hidden md:flex space-x-6 font-body text-foreground">
          <Link to="/" className="hover:text-primary">Home</Link>
          <Link to="/about" className="hover:text-primary">About</Link>
          <Link to="/services" className="hover:text-primary">Services</Link>
          <Link to="/contact" className="hover:text-primary">Contact</Link>
        </nav>
        <button className="md:hidden text-foreground" onClick={() => setOpen(!open)}>☰</button>
      </div>
      {open && (
        <div className="md:hidden bg-background border-t">
          <Link to="/" className="block px-4 py-2 hover:bg-gray-100">Home</Link>
          <Link to="/about" className="block px-4 py-2 hover:bg-gray-100">About</Link>
          <Link to="/services" className="block px-4 py-2 hover:bg-gray-100">Services</Link>
          <Link to="/contact" className="block px-4 py-2 hover:bg-gray-100">Contact</Link>
        </div>
      )}
    </header>
  );
}""",
            "Footer": """import React from 'react';

export default function Footer() {
  return (
    <footer className="bg-background border-t py-6 mt-10">
      <div className="max-w-6xl mx-auto px-4 flex flex-col md:flex-row justify-between items-center text-sm text-foreground">
        <div className="mb-4 md:mb-0">© {new Date().getFullYear()} MySite. All rights reserved.</div>
        <div className="space-x-4">
          <a href="#" className="hover:text-primary">Privacy Policy</a>
          <a href="#" className="hover:text-primary">Terms of Service</a>
          <a href="/contact" className="hover:text-primary">Contact</a>
        </div>
      </div>
    </footer>
  );
}""",

            "Hero": """import React from 'react';

export default function Hero() {
  return (
    <section className="min-h-screen flex items-center justify-center bg-gradient-to-r from-primary to-blue-600 text-white">
      <div className="text-center px-4">
        <h1 className="text-5xl font-bold font-heading mb-6">Welcome to Our Website</h1>
        <p className="text-xl mb-8 font-body max-w-2xl">
          Discover amazing features and services that will transform your experience
        </p>
        <button className="bg-white text-primary px-8 py-3 rounded-lg font-semibold hover:bg-gray-100 transition">
          Get Started
        </button>
      </div>
    </section>
  );
}""",
            
            "FeatureGrid": """import React from 'react';

export default function FeatureGrid() {
  const features = [
    { title: "Fast & Reliable", description: "Lightning-fast performance you can count on", icon: "⚡" },
    { title: "Secure", description: "Enterprise-grade security for your peace of mind", icon: "🔒" },
    { title: "Easy to Use", description: "Intuitive interface designed for everyone", icon: "🎯" },
    { title: "24/7 Support", description: "Round-the-clock assistance when you need it", icon: "🎧" }
  ];

  return (
    <section className="py-20 px-4 bg-background">
      <div className="max-w-6xl mx-auto">
        <h2 className="text-4xl font-bold font-heading text-center mb-16 text-foreground">
          Why Choose Us
        </h2>
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
          {features.map((feature, index) => (
            <div key={index} className="text-center p-6 rounded-lg hover:shadow-lg transition">
              <div className="text-4xl mb-4">{feature.icon}</div>
              <h3 className="text-xl font-semibold font-heading mb-3 text-foreground">
                {feature.title}
              </h3>
              <p className="font-body text-gray-600">{feature.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}""",

            "ContactForm": """import React from 'react';

export default function ContactForm() {
  return (
    <section className="py-20 px-4 bg-gray-50">
      <div className="max-w-2xl mx-auto">
        <h2 className="text-4xl font-bold font-heading text-center mb-16 text-foreground">
          Get In Touch
        </h2>
        <form className="bg-white p-8 rounded-lg shadow-lg">
          <div className="mb-6">
            <label className="block text-sm font-semibold mb-2 text-foreground">Name</label>
            <input 
              type="text" 
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-primary"
              placeholder="Your Name"
            />
          </div>
          <div className="mb-6">
            <label className="block text-sm font-semibold mb-2 text-foreground">Email</label>
            <input 
              type="email" 
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-primary"
              placeholder="your@email.com"
            />
          </div>
          <div className="mb-6">
            <label className="block text-sm font-semibold mb-2 text-foreground">Message</label>
            <textarea 
              rows="4"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-primary"
              placeholder="Your message..."
            ></textarea>
          </div>
          <button 
            type="submit" 
            className="w-full bg-primary text-white py-3 rounded-lg font-semibold hover:bg-blue-700 transition"
          >
            Send Message
          </button>
        </form>
      </div>
    </section>
  );
}""",

            "ProductGrid": """import React from 'react';

export default function ProductGrid() {
  const products = [
    { title: "Product 1", description: "Amazing product description", price: "$99" },
    { title: "Product 2", description: "Another great product", price: "$149" },
    { title: "Product 3", description: "Premium product option", price: "$199" },
    { title: "Product 4", description: "Budget-friendly choice", price: "$49" },
    { title: "Product 5", description: "Professional solution", price: "$299" },
    { title: "Product 6", description: "Enterprise package", price: "$499" }
  ];

  return (
    <section className="py-20 px-4 bg-background">
      <div className="max-w-6xl mx-auto">
        <h2 className="text-4xl font-bold font-heading text-center mb-16 text-foreground">
          Our Products
        </h2>
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {products.map((product, index) => (
            <div key={index} className="bg-white p-6 rounded-lg shadow-lg hover:shadow-xl transition">
              <div className="h-48 bg-gray-200 rounded-lg mb-4"></div>
              <h3 className="text-xl font-semibold font-heading mb-3 text-foreground">
                {product.title}
              </h3>
              <p className="font-body text-gray-600 mb-4">{product.description}</p>
              <div className="flex justify-between items-center">
                <span className="text-2xl font-bold text-primary">{product.price}</span>
                <button className="bg-primary text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition">
                  Buy Now
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}""",

            "Testimonials": """import React from 'react';

export default function Testimonials() {
  const testimonials = [
    { quote: "Absolutely amazing service!", author: "John Doe", title: "CEO, Company Inc" },
    { quote: "Exceeded all expectations.", author: "Jane Smith", title: "Marketing Director" },
    { quote: "Highly recommend to everyone!", author: "Mike Johnson", title: "Freelancer" }
  ];

  return (
    <section className="py-20 px-4 bg-gray-50">
      <div className="max-w-6xl mx-auto">
        <h2 className="text-4xl font-bold font-heading text-center mb-16 text-foreground">
          What Our Clients Say
        </h2>
        <div className="grid md:grid-cols-3 gap-8">
          {testimonials.map((testimonial, index) => (
            <div key={index} className="bg-white p-6 rounded-lg shadow-lg">
              <div className="text-yellow-400 mb-4">★★★★★</div>
              <p className="font-body text-gray-600 mb-4 italic">"{testimonial.quote}"</p>
              <div>
                <div className="font-semibold text-foreground">{testimonial.author}</div>
                <div className="text-sm text-gray-500">{testimonial.title}</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}""",

            "Pricing": """import React from 'react';

export default function Pricing() {
  const plans = [
    { name: "Basic", price: "$9", features: ["Feature 1", "Feature 2", "Feature 3"] },
    { name: "Pro", price: "$19", features: ["Everything in Basic", "Feature 4", "Feature 5"], popular: true },
    { name: "Enterprise", price: "$39", features: ["Everything in Pro", "Feature 6", "Feature 7"] }
  ];

  return (
    <section className="py-20 px-4 bg-background">
      <div className="max-w-6xl mx-auto">
        <h2 className="text-4xl font-bold font-heading text-center mb-16 text-foreground">
          Choose Your Plan
        </h2>
        <div className="grid md:grid-cols-3 gap-8">
          {plans.map((plan, index) => (
            <div key={index} className={`bg-white p-8 rounded-lg shadow-lg ${plan.popular ? 'ring-2 ring-primary' : ''}`}>
              {plan.popular && (
                <div className="bg-primary text-white px-3 py-1 rounded-full text-sm mb-4 inline-block">
                  Most Popular
                </div>
              )}
              <h3 className="text-2xl font-bold font-heading mb-4 text-foreground">{plan.name}</h3>
              <div className="text-4xl font-bold text-primary mb-6">{plan.price}<span className="text-lg text-gray-500">/mo</span></div>
              <ul className="space-y-3 mb-8">
                {plan.features.map((feature, i) => (
                  <li key={i} className="flex items-center font-body text-gray-600">
                    <span className="text-green-500 mr-3">✓</span>
                    {feature}
                  </li>
                ))}
              </ul>
              <button className="w-full bg-primary text-white py-3 rounded-lg font-semibold hover:bg-blue-700 transition">
                Get Started
              </button>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}""",

            "FAQ": """import React from 'react';

export default function FAQ() {
  const faqs = [
    { question: "What is your service about?", answer: "We provide amazing solutions for your business needs." },
    { question: "How much does it cost?", answer: "We offer flexible pricing plans to suit different budgets." },
    { question: "Is there a free trial?", answer: "Yes, we offer a 14-day free trial with full features." },
    { question: "How do I get started?", answer: "Simply sign up and follow our quick setup guide." },
    { question: "Do you offer support?", answer: "We provide 24/7 customer support via chat and email." },
    { question: "Can I cancel anytime?", answer: "Yes, you can cancel your subscription at any time." }
  ];

  return (
    <section className="py-20 px-4 bg-gray-50">
      <div className="max-w-4xl mx-auto">
        <h2 className="text-4xl font-bold font-heading text-center mb-16 text-foreground">
          Frequently Asked Questions
        </h2>
        <div className="space-y-4">
          {faqs.map((faq, index) => (
            <details key={index} className="bg-white p-6 rounded-lg shadow">
              <summary className="font-semibold font-heading text-foreground cursor-pointer">
                {faq.question}
              </summary>
              <p className="mt-4 font-body text-gray-600">{faq.answer}</p>
            </details>
          ))}
        </div>
      </div>
    </section>
  );
}""",

            "RichText": """import React from 'react';

export default function RichText() {
  return (
    <section className="py-20 px-4 bg-background">
      <div className="max-w-4xl mx-auto">
        <h2 className="text-4xl font-bold font-heading mb-8 text-foreground">
          About Our Company
        </h2>
        <div className="prose prose-lg max-w-none">
          <p className="font-body text-gray-600 mb-6">
            We are a leading company dedicated to providing exceptional services and solutions 
            to our clients worldwide. Our team of experts works tirelessly to ensure your 
            success and satisfaction.
          </p>
          <h3 className="text-2xl font-semibold font-heading mb-4 text-foreground">Our Mission</h3>
          <p className="font-body text-gray-600 mb-6">
            To deliver innovative solutions that empower businesses and individuals to achieve 
            their goals while maintaining the highest standards of quality and service.
          </p>
          <h3 className="text-2xl font-semibold font-heading mb-4 text-foreground">Our Values</h3>
          <ul className="font-body text-gray-600 space-y-2">
            <li>• Excellence in everything we do</li>
            <li>• Innovation and continuous improvement</li>
            <li>• Customer satisfaction as our priority</li>
            <li>• Integrity and transparency in our operations</li>
          </ul>
        </div>
      </div>
    </section>
  );
}""",

            "CTA": """import React from 'react';

export default function CTA() {
  return (
    <section className="py-20 px-4 bg-primary text-white">
      <div className="max-w-4xl mx-auto text-center">
        <h2 className="text-4xl font-bold font-heading mb-6">
          Ready to Get Started?
        </h2>
        <p className="text-xl font-body mb-8 opacity-90">
          Join thousands of satisfied customers who trust our services. 
          Start your journey today and experience the difference.
        </p>
        <button className="bg-white text-primary px-8 py-4 rounded-lg font-semibold text-lg hover:bg-gray-100 transition">
          Start Free Trial
        </button>
      </div>
    </section>
  );
}"""
        }
        
        return fallbacks.get(section_type, f"""import React from 'react';

export default function {section_type}() {{
  return (
    <section className="py-20 px-4">
      <div className="max-w-4xl mx-auto text-center">
        <h2 className="text-3xl font-bold font-heading mb-8 text-foreground">
          {section_type} Section
        </h2>
        <p className="font-body text-gray-600">
          This is a {section_type.lower()} section. Content coming soon.
        </p>
      </div>
    </section>
  );
}}""")

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
                f.write(self.generate_app_component(spec.pages))
            
            # Generate components - create unique components for each page
            generated_components = set()
            
            for page in spec.pages:
                page_name = page.route.replace('/', '').title() or 'Home'
                
                # Generate unique Header and Footer for non-Home pages
                if page_name != 'Home':
                    # Generate unique Header
                    header_name = f"{page_name}Header"
                    if header_name not in generated_components:
                        header_code = self.get_fallback_component("Header").replace("export default function Header()", f"export default function {header_name}()")
                        with open(os.path.join(components_dir, f'{header_name}.jsx'), 'w', encoding='utf-8') as f:
                            f.write(header_code)
                        generated_components.add(header_name)
                    
                    # Generate unique Footer
                    footer_name = f"{page_name}Footer"
                    if footer_name not in generated_components:
                        footer_code = self.get_fallback_component("Footer").replace("export default function Footer()", f"export default function {footer_name}()")
                        with open(os.path.join(components_dir, f'{footer_name}.jsx'), 'w', encoding='utf-8') as f:
                            f.write(footer_code)
                        generated_components.add(footer_name)
                else:
                    # Generate standard Header and Footer for Home page
                    if "Header" not in generated_components:
                        header_code = self.get_fallback_component("Header")
                        with open(os.path.join(components_dir, 'Header.jsx'), 'w', encoding='utf-8') as f:
                            f.write(header_code)
                        generated_components.add("Header")
                    
                    if "Footer" not in generated_components:
                        footer_code = self.get_fallback_component("Footer")
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
                        
                        if section.type in ['Header', 'Footer']:
                            # Use fallback for Header/Footer sections
                            component_code = self.get_fallback_component(section.type)
                        else:
                            # Generate custom component
                            component_code = self.generate_component(section, spec.designTokens.model_dump())
                        
                        # Ensure component_code is a string
                        if not isinstance(component_code, str):
                            print(f"Warning: Component code for {component_name} is not a string: {type(component_code)}")
                            component_code = self.get_fallback_component(section.type)
                        
                        # Update component name in code if it's a page-specific component
                        if page_name != 'Home' and section.type not in ['Header', 'Footer']:
                            component_code = component_code.replace(f"export default function {section.type}()", f"export default function {component_name}()")
                        
                        with open(os.path.join(components_dir, f'{component_name}.jsx'), 'w', encoding='utf-8') as f:
                            f.write(component_code)
                        generated_components.add(component_name)
                        generated_components.add(section.type)
            
            # Generate pages
            for page in spec.pages:
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