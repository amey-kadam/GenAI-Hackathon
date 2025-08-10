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
- Make sure the component is complete and functional
- Include all necessary imports (React, useState if needed)
"""

        specific_requirements = {
            "Header": """
- A sticky navigation bar with logo on the left and navigation links on the right
- Mobile-friendly hamburger menu with state management
- Use Tailwind CSS only
- Use colors from design tokens for background and text
- Include links: Home, About, Services, Contact
- Modern, clean style
- Responsive menu that toggles on mobile
""",
            "Footer": """
- Footer with company name/logo on the left
- Links: Privacy Policy, Terms of Service, Contact
- Responsive design
- Use Tailwind CSS only
- Small text copyright with current year
- Background color from design tokens
- Professional spacing and layout
""",
            "Hero": """
- Large hero section with gradient background
- Main headline and compelling subheadline  
- Call-to-action button
- Full viewport height or near-full height
- Centered content with good typography
- Modern, engaging design
""",
            "FeatureGrid": """
- Grid of 3-4 feature cards
- Each card has icon (use emoji or simple text), title, description
- Responsive grid (1 col mobile, 2-3 cols desktop)
- Clean card design with hover effects
- Professional spacing and typography
- Use design token colors
""",
            "ProductGrid": """
- Grid of 6-9 product/project cards
- Each card has image placeholder, title, description, price/link
- Responsive grid layout (1 col mobile, 2-3 cols desktop)
- Hover effects and transitions
- Professional card styling with buttons
""",
            "Testimonials": """
- 3 testimonial cards in a row
- Each with quote, author name, author title/company
- Star ratings or review indicators
- Clean card design with proper spacing
- Responsive layout (stacks on mobile)
""",
            "Pricing": """
- 2-3 pricing tiers side by side
- Each tier with title, price, features list, CTA button
- Highlight popular/recommended plan with different styling
- Responsive stacking on mobile
- Professional pricing card design
""",
            "FAQ": """
- 6-8 frequently asked questions
- Use details/summary HTML elements for expand/collapse
- Clean typography and spacing
- Professional FAQ design
- Good user experience
""",
            "RichText": """
- Well-formatted content section with multiple headings and paragraphs
- Mix of h2, h3 headings, paragraphs, and lists
- Professional typography using design token fonts
- Good reading experience with proper spacing
- Content hierarchy and responsive design
""",
            "ContactForm": """
- Form with name, email, message fields and labels
- Professional styling with focus states
- Submit button with hover effects
- Form validation styling (border colors)
- Responsive design
- Good form UX
""",
            "CTA": """
- Call-to-action section with compelling headline
- Brief description text
- Primary action button
- Eye-catching design with background
- Centered layout
- Strong visual impact
"""
        }

        full_prompt = base_prompt + specific_requirements.get(section_type, f"Create a professional {section_type} section component.")
        
        response = self.model.generate_content(full_prompt)
        return response.text.strip()

    def generate_simple_component(self, section_type: str, design_tokens: Dict[str, Any]) -> str:
        """Generate a simpler component with a more basic prompt"""
        simple_prompt = f"""
Create a React component called {section_type} using Tailwind CSS.
Use these colors: primary='{design_tokens.get('colors', {}).get('primary', '#3B82F6')}', background='{design_tokens.get('colors', {}).get('background', '#FFFFFF')}', foreground='{design_tokens.get('colors', {}).get('foreground', '#111111')}'

Make it responsive and professional. Return only the JSX code with imports.
Component should be a {section_type.lower()} section with appropriate content.
"""
        
        response = self.model.generate_content(simple_prompt)
        return self.clean_component_response(response.text.strip())

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

    def clean_component_response(self, response: str) -> str:
        """Clean up the API response to extract just the component code"""
        # Remove markdown code blocks if present
        if "```" in response:
            lines = response.split('\n')
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
            
            response = '\n'.join(lines[start_idx:end_idx])
        
        # Clean Unicode characters
        response = self.clean_unicode(response.strip())
        return response

    def generate_component(self, section_type: str, design_tokens: Dict[str, Any], props: Dict[str, Any] = None) -> str:
        """Generate a component using Gemini API"""
        try:
            component_code = self.get_component_template(section_type, design_tokens)
            
            # Clean up the response
            component_code = self.clean_component_response(component_code)
            
            # Validate that we got a reasonable response
            if not component_code or len(component_code) < 100:
                print(f"Response too short for {section_type}, retrying with simple prompt...")
                component_code = self.generate_simple_component(section_type, design_tokens)
            
            return component_code
            
        except Exception as e:
            print(f"Error generating {section_type} component: {e}")
            # Try with simple prompt as fallback
            try:
                return self.generate_simple_component(section_type, design_tokens)
            except Exception as retry_error:
                print(f"Retry failed for {section_type}: {retry_error}")
                raise Exception(f"Failed to generate component {section_type} after all retries")