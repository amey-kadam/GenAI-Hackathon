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

    def get_fallback_component(self, section_type: str) -> str:
        """Fallback components if API fails"""
        fallbacks = {
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
    { title: "Fast & Reliable", description: "Lightning-fast performance you can count on", icon: "Lightning" },
    { title: "Secure", description: "Enterprise-grade security for your peace of mind", icon: "Security" },
    { title: "Easy to Use", description: "Intuitive interface designed for everyone", icon: "Target" },
    { title: "24/7 Support", description: "Round-the-clock assistance when you need it", icon: "Support" }
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
              <div className="text-2xl font-bold mb-4 text-primary">{feature.icon}</div>
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