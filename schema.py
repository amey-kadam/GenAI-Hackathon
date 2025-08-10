from typing import List, Literal, Optional, Dict, Any
from pydantic import BaseModel, Field
import uuid

SectionType = Literal[
    "Hero", "FeatureGrid", "ProductGrid", "Testimonials", "Pricing", "FAQ", "RichText", "ContactForm", "CTA"
]

class DesignTokens(BaseModel):
    colors: Dict[str, str] = {"primary": "#C62828", "background": "#ffffff", "foreground": "#111111"}
    font: Dict[str, str] = {"heading": "Inter", "body": "Inter"}
    radius: str = "12px"
    spacingScale: Literal["tight", "normal", "roomy"] = "tight"
    typeScale: Literal["sm", "md", "lg"] = "md"

class Section(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: SectionType
    props: Dict[str, Any] = {}

class Page(BaseModel):
    route: str
    seo: Optional[Dict[str, str]] = None
    sections: List[Section] = []

class Spec(BaseModel):
    project: Dict[str, str] = {"name": "Mini-Lovable App", "stack": "flask"}
    designTokens: DesignTokens = DesignTokens()
    pages: List[Page] = []