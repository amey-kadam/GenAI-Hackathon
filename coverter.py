import os
from typing import Any, Dict
from schema import Spec, Page, Section, DesignTokens

# ---------- Fallback (no-LLM) rules ----------

def _pick_color(prompt: str) -> str:
    p = prompt.lower()
    if "blue" in p: return "#1E3A8A"
    if "green" in p: return "#166534"
    if "purple" in p: return "#6D28D9"
    if "black" in p or "dark" in p: return "#111111"
    if "red" in p or "maroon" in p: return "#C62828"
    return "#0F766E"  # teal default


def _pick_font(prompt: str) -> Dict[str, str]:
    p = prompt.lower()
    if "serif" in p: return {"heading": "Merriweather", "body": "Merriweather"}
    if "mono" in p: return {"heading": "JetBrains Mono", "body": "JetBrains Mono"}
    return {"heading": "Inter", "body": "Inter"}


def _pick_spacing(prompt: str) -> str:
    p = prompt.lower()
    if "compact" in p or "tight" in p: return "tight"
    if "spacious" in p or "airy" in p or "roomy" in p: return "roomy"
    return "normal"


def naive_spec_from_prompt(prompt: str) -> Spec:
    p = prompt.lower()

    tokens = DesignTokens()
    tokens.colors["primary"] = _pick_color(prompt)
    tokens.font = _pick_font(prompt)
    tokens.spacingScale = _pick_spacing(prompt)
    tokens.typeScale = "lg" if ("big typography" in p or "bold headings" in p) else "md"

    wants_products = any(k in p for k in ["product", "store", "catalog", "shop"])
    wants_testimonials = "testimonial" in p
    wants_faq = "faq" in p
    wants_contact = "contact" in p or "reach us" in p
    wants_pricing = "pricing" in p or "plans" in p
    wants_about = any(k in p for k in ["about", "company", "who we are"])

    pages = []

    # HOME
    home_sections = [
        Section(type="Hero", props={
            "headline": "Built from your prompt",
            "sub": "Generated in seconds with consistent styling.",
            "cta": {"label": "Get Started", "href": "/contact" if wants_contact else "#"}
        })
    ]
    if wants_products:
        home_sections.append(Section(type="ProductGrid", props={"count": 8}))
    home_sections.append(Section(type="FeatureGrid", props={"items": ["Fast", "Consistent", "Mobile-first"]}))
    if wants_pricing:
        home_sections.append(Section(type="Pricing", props={"plans": ["Starter", "Pro", "Team"]}))
    if wants_testimonials:
        home_sections.append(Section(type="Testimonials", props={}))
    if wants_faq:
        home_sections.append(Section(type="FAQ", props={}))
    pages.append(Page(route="/", seo={"title": "Home", "description": "Landing"}, sections=home_sections))

    # ABOUT
    if wants_about:
        pages.append(Page(route="/about", sections=[Section(type="RichText", props={"html": "<p>About us…</p>"})]))

    # CONTACT
    if wants_contact:
        pages.append(Page(route="/contact", sections=[Section(type="ContactForm", props={})]))

    # Default minimal contact if nothing requested
    if not wants_about and not wants_contact:
        pages.append(Page(route="/contact", sections=[Section(type="ContactForm", props={})]))

    return Spec(pages=pages, designTokens=tokens)

# ---------- Gemini-backed converter ----------

def gemini_spec_from_prompt(prompt: str) -> Spec:
    import google.generativeai as genai
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return naive_spec_from_prompt(prompt)

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-pro")

    schema = {
        "type": "object",
        "properties": {
            "project": {"type": "object"},
            "designTokens": {
                "type": "object",
                "properties": {
                    "colors": {"type": "object"},
                    "font": {"type": "object"},
                    "radius": {"type": "string"},
                    "spacingScale": {"type": "string"},
                    "typeScale": {"type": "string"}
                },
                "required": ["colors", "font", "radius", "spacingScale", "typeScale"]
            },
            "pages": {"type": "array"}
        },
        "required": ["designTokens", "pages"]
    }

    prompt_text = (
        "You are a JSON generator. Convert the user's website prompt into a Spec JSON with designTokens and pages. "
        "Use concise defaults if missing. Return ONLY JSON."
    )

    resp = model.generate_content([
        {"text": prompt_text},
        {"text": f"User prompt: {prompt}"}
    ])

    # Attempt to parse JSON; if anything fails, fallback
    import json
    try:
        raw = resp.candidates[0].content.parts[0].text.strip()
        data = json.loads(raw)
        return Spec(**data)
    except Exception:
        return naive_spec_from_prompt(prompt)