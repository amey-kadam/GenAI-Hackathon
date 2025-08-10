import os
import json
import re
import uuid
from schema import Spec, Page, Section

def _strip_code_fences(s: str) -> str:
    s = s.strip()
    if s.startswith("```"):
        s = re.sub(r"^```(?:json)?\s*|\s*```$", "", s, flags=re.S)
    return s.strip()

INSTRUCTIONS = (
    "You are a strict JSON generator for a website scaffold. "
    "Given a short English prompt, output a Spec JSON with this structure: "
    "{ project, designTokens, pages[] }. "
    "Design tokens must include colors {primary, background, foreground}, "
    "font {heading, body}, radius, spacingScale (tight|normal|roomy), typeScale (sm|md|lg). "
    "Infer a website archetype (Generic/Company, E-commerce, SaaS, Portfolio, Restaurant, Clinic, Blog). "
    "Then produce 5–7 sensible pages for that archetype. Always include Home and Contact, usually About. "
    "Each page must have: route (URL path like '/about'), seo: {title, description}, and sections array. "
    "Each section must be an object with: type (Hero|FeatureGrid|ProductGrid|Testimonials|Pricing|FAQ|RichText|ContactForm|CTA|Header|Footer), id (UUID), and props (object). "
    "Provide basic SEO (title, description) for each page. "
    "Prefer mobile-first structure. Use concise defaults when information is missing. "
    "Return ONLY valid JSON, no comments, no markdown fences."
)

def _normalize_data(data: dict) -> dict:
    if 'pages' in data:
        normalized_pages = []

        # Ensure required pages exist
        required_routes = [('/', 'Home'), ('/about', 'About'), ('/services', 'Services'), ('/contact', 'Contact')]
        existing_routes = {p.get('route', '').lower() for p in data['pages']}

        for route, name in required_routes:
            if route not in existing_routes:
                data['pages'].append({
                    'route': route,
                    'seo': {'title': name, 'description': f'{name} page'},
                    'sections': [{'id': str(uuid.uuid4()), 'type': 'Hero', 'props': {}}]
                })

        # Add Header & Footer to each page
        for page in data['pages']:
            if not any(s.get('type') == 'Header' for s in page['sections']):
                page['sections'].insert(0, {'id': str(uuid.uuid4()), 'type': 'Header', 'props': {}})
            if not any(s.get('type') == 'Footer' for s in page['sections']):
                page['sections'].append({'id': str(uuid.uuid4()), 'type': 'Footer', 'props': {}})

        # Normalize sections for schema compliance
        for page in data['pages']:
            normalized_page = {}
            normalized_page['route'] = page.get('route', '/')
            normalized_page['seo'] = page.get('seo', {'title': page.get('name', ''), 'description': f"{page.get('name', '')} page"})
            normalized_sections = []
            for section in page.get('sections', []):
                if isinstance(section, str):
                    section_type = section
                    if section_type not in ['Hero', 'FeatureGrid', 'ProductGrid', 'Testimonials', 'Pricing', 'FAQ', 'RichText', 'ContactForm', 'CTA', 'Header', 'Footer']:
                        section_type = 'RichText'
                    normalized_sections.append({'id': str(uuid.uuid4()), 'type': section_type, 'props': {}})
                elif isinstance(section, dict):
                    if 'id' not in section:
                        section['id'] = str(uuid.uuid4())
                    if 'props' not in section:
                        section['props'] = {}
                    normalized_sections.append(section)
            normalized_page['sections'] = normalized_sections
            normalized_pages.append(normalized_page)

        data['pages'] = normalized_pages

    return data

def gemini_spec_from_prompt(prompt: str) -> Spec:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is missing.")

    import google.generativeai as genai
    genai.configure(api_key=api_key)

    model = genai.GenerativeModel(
        model_name="gemini-1.5-pro",
        system_instruction=INSTRUCTIONS,
        generation_config={"response_mime_type": "application/json"},
    )

    resp = model.generate_content([{"text": prompt}])
    raw = getattr(resp, "text", "") or resp.candidates[0].content.parts[0].text
    raw = _strip_code_fences(raw)
    data = json.loads(raw)

    # Normalize the data to match our schema
    data = _normalize_data(data)

    return Spec(**data)
