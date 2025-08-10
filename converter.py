import os
import json
import re
import uuid
from schema import Spec, Page, Section

# Gemini-only converter: takes a natural-language prompt and returns Spec JSON
# Requires GEMINI_API_KEY to be set. No local fallback.

def _strip_code_fences(s: str) -> str:
    s = s.strip()
    if s.startswith("```"):
        # remove ```json ... ``` or ``` ... ```
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
    "Each section must be an object with: type (Hero|FeatureGrid|ProductGrid|Testimonials|Pricing|FAQ|RichText|ContactForm|CTA), id (UUID), and props (object). "
    "Provide basic SEO (title, description) for each page. "
    "Prefer mobile-first structure. Use concise defaults when information is missing. "
    "Return ONLY valid JSON, no comments, no markdown fences."
)

def _normalize_data(data: dict) -> dict:
    """Normalize the Gemini response to match our schema"""
    # Normalize pages
    if 'pages' in data:
        normalized_pages = []
        for page in data['pages']:
            normalized_page = {}
            
            # Handle route field
            if 'route' not in page:
                if 'name' in page:
                    # Convert name to route
                    route = page['name'].lower().replace(' ', '-')
                    if route == 'home':
                        route = '/'
                    else:
                        route = f'/{route}'
                    normalized_page['route'] = route
                else:
                    normalized_page['route'] = '/'
            else:
                normalized_page['route'] = page['route']
            
            # Handle SEO
            if 'seo' in page:
                normalized_page['seo'] = page['seo']
            elif 'name' in page:
                # Generate basic SEO from name
                normalized_page['seo'] = {
                    'title': page['name'],
                    'description': f'{page["name"]} page'
                }
            
            # Handle sections
            normalized_sections = []
            if 'sections' in page:
                for section in page['sections']:
                    if isinstance(section, str):
                        # Convert string to section object
                        # Handle special case where Gemini might return unsupported section types
                        section_type = section
                        if section_type == 'ProjectGrid':
                            section_type = 'ProductGrid'  # Map to supported type
                        elif section_type == 'FeaturedProjects':
                            section_type = 'ProductGrid'  # Map to supported type
                        elif section_type not in ['Hero', 'FeatureGrid', 'ProductGrid', 'Testimonials', 'Pricing', 'FAQ', 'RichText', 'ContactForm', 'CTA']:
                            section_type = 'RichText'  # Default fallback
                        
                        normalized_section = {
                            'id': str(uuid.uuid4()),
                            'type': section_type,
                            'props': {}
                        }
                        normalized_sections.append(normalized_section)
                    elif isinstance(section, dict):
                        # Already in correct format, just ensure it has required fields
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