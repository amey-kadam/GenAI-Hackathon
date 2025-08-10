import os
import json
from typing import Dict, Any
import google.generativeai as genai

class ComponentGenerator:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-1.5-pro")

    def get_component_template(self, section_type: str, design_tokens: Dict[str, Any]) -> str:
        """Get a more specific template for each component type"""
        
        base_prompt = f"""
Create a modern, professional React component for a {section_type} section.
Use ONLY Tailwind CSS classes for styling.
Use these design tokens: {json.dumps(design_tokens, indent=2)}

Requirements:
- Component name: {section_type}
- Export as default
- Fully responsive design
- Modern UI/UX patterns
- Use design token colors: primary, background, foreground
- Use design token fonts: heading, body
- Professional spacing and layout
- Return ONLY the JSX component code, no explanations or markdown
"""

        specific_requirements = {
          "Header": """
- A sticky navigation bar with logo on the left and navigation links on the right
- Mobile-friendly hamburger menu
- Use Tailwind CSS only
- Use colors from design tokens for background and text
- Include links: Home, About, Services, Contact
- Modern, clean style
""",
"Footer": """
- Footer with company name/logo on the left
- Links: Privacy Policy, Terms of Service, Contact
- Responsive design
- Use Tailwind CSS only
- Small text copyright
- Background color from design tokens
""",

            "Hero": """
- Large hero section with background
- Main headline and subheadline  
- Call-to-action button
- Optional hero image or graphic
- Full viewport height
- Centered content
""",
            "FeatureGrid": """
- Grid of 3-4 feature cards
- Each card has icon, title, description
- Responsive grid (1 col mobile, 2-3 cols desktop)
- Clean card design with hover effects
- Use placeholder icons (emoji or simple shapes)
""",
            "ProductGrid": """
- Grid of 6-9 product/project cards
- Each card has image, title, description, price/link
- Responsive grid layout
- Hover effects and transitions
- Professional card styling
""",
            "Testimonials": """
- 3 testimonial cards in a row
- Each with quote, author name, author title/company
- Star ratings
- Clean card design
- Responsive layout
""",
            "Pricing": """
- 2-3 pricing tiers side by side
- Each tier with title, price, features list, CTA button
- Highlight popular/recommended plan
- Responsive stacking on mobile
""",
            "FAQ": """
- 6-8 frequently asked questions
- Expandable/collapsible design
- Clean typography
- Proper spacing between items
- Use details/summary or button toggle
""",
            "RichText": """
- Well-formatted content section
- Mix of headings, paragraphs, lists
- Professional typography
- Good reading experience
- Proper spacing and hierarchy
""",
            "ContactForm": """
- Form with name, email, message fields
- Professional styling
- Submit button
- Form validation styling
- Responsive design
""",
            "CTA": """
- Call-to-action section
- Compelling headline
- Brief description
- Primary action button
- Eye-catching design
- Centered layout
"""
        }

        full_prompt = base_prompt + specific_requirements.get(section_type, "")
        
        response = self.model.generate_content(full_prompt)
        return response.text.strip()

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
            '💰': 'Money'
        }
        
        for unicode_char, replacement in replacements.items():
            text = text.replace(unicode_char, replacement)
        return text

    def generate_component(self, section_type: str, design_tokens: Dict[str, Any], props: Dict[str, Any] = None) -> str:
        """Generate a component with better templates"""
        try:
            component_code = self.get_component_template(section_type, design_tokens)
            
            # Clean up the response (remove markdown code blocks if present)
            if "```" in component_code:
                lines = component_code.split('\n')
                start_idx = 0
                end_idx = len(lines)
                
                for i, line in enumerate(lines):
                    if line.strip().startswith('```'):
                        start_idx = i + 1
                        break
                
                for i in range(len(lines) - 1, -1, -1):
                    if lines[i].strip() == '```':
                        end_idx = i
                        break
                
                component_code = '\n'.join(lines[start_idx:end_idx])
            
            # Clean Unicode characters
            component_code = self.clean_unicode(component_code.strip())
            return component_code
            
        except Exception as e:
            # Fallback to basic template if generation fails
            print(f"Error generating {section_type} component: {e}")
            return self.get_fallback_component(section_type)

