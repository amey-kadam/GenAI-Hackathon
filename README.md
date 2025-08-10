# 🚀 AI Website Generator

An intelligent website generator that creates complete, production-ready React websites from natural language descriptions using Google's Gemini AI.

## ✨ Features

- **Natural Language Input**: Describe your website in plain English
- **Complete Project Generation**: Get a full React + Vite + Tailwind CSS project
- **Modern Tech Stack**: Uses latest web development best practices
- **Responsive Design**: Mobile-first, fully responsive websites
- **Custom Design Tokens**: Automatically generates color schemes, fonts, and spacing
- **Multiple Page Types**: Supports various page layouts and components
- **Download & Run**: Get a ZIP file ready for immediate development

## 🛠️ Tech Stack

### Backend
- **Flask** - Python web framework
- **Google Gemini AI** - For intelligent code generation
- **Pydantic** - Data validation and schema management

### Generated Websites
- **React 18** - Modern React with hooks
- **Vite** - Fast build tool and dev server
- **Tailwind CSS** - Utility-first CSS framework
- **React Router** - Client-side routing

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Google Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd ai-website-generator
   ```

2. **Run the setup script**
   ```bash
   python setup.py
   ```

3. **Configure your API key**
   - Open the `.env` file
   - Replace `your_gemini_api_key_here` with your actual Gemini API key:
     ```
     GEMINI_API_KEY=your_actual_api_key_here
     ```

4. **Start the server**
   ```bash
   python app.py
   ```

5. **Open your browser**
   - Navigate to `http://localhost:5000`
   - Start generating websites!

### Manual Installation (if setup.py fails)

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Create environment file**
   ```bash
   cp .env.example .env
   # Edit .env and add your Gemini API key
   ```

3. **Create templates directory**
   ```bash
   mkdir templates
   ```

## 🎯 How to Use

1. **Describe Your Website**
   - Enter a natural language description of the website you want
   - Example: "Create a modern portfolio website for a software developer with dark theme, project showcase, and contact form"

2. **Wait for Generation**
   - The AI analyzes your requirements
   - Generates website structure and components
   - Creates all necessary files

3. **Download Your Website**
   - Get a ZIP file with your complete project
   - Extract it to your desired location

4. **Run Your Website**
   ```bash
   cd your-website-folder
   npm install
   npm run dev
   ```

## 📁 Generated Project Structure

```
your-website/
├── package.json          # Dependencies and scripts
├── vite.config.js        # Vite configuration
├── tailwind.config.js    # Tailwind with custom design tokens
├── postcss.config.js     # PostCSS configuration
├── index.html           # Main HTML file
├── README.md            # Project documentation
└── src/
    ├── main.jsx         # App entry point
    ├── App.jsx          # Main app component with routing
    ├── index.css        # Global styles with Tailwind
    ├── components/      # Reusable components
    │   ├── Hero.jsx
    │   ├── FeatureGrid.jsx
    │   ├── ContactForm.jsx
    │   └── ...
    └── pages/           # Page components
        ├── HomePage.jsx
        ├── AboutPage.jsx
        ├── ContactPage.jsx
        └── ...
```

## 🧩 Supported Components

The generator can create various types of components:

- **Hero**: Landing page hero sections
- **FeatureGrid**: Feature showcases in grid layout
- **ProductGrid**: Product or project galleries
- **Testimonials**: Customer testimonials
- **Pricing**: Pricing tables and plans
- **FAQ**: Frequently asked questions
- **ContactForm**: Contact forms with validation
- **RichText**: Content sections with rich formatting
- **CTA**: Call-to-action sections

## 🎨 Supported Website Types

- **Portfolio**: Personal or professional portfolios
- **Company**: Business websites
- **E-commerce**: Online stores
- **SaaS**: Software as a Service landing pages
- **Restaurant**: Restaurant and food service sites
- **Clinic**: Healthcare and medical sites
- **Blog**: Content and blogging platforms

## ⚙️ Configuration

### Design Tokens
Each generated website includes custom design tokens:

- **Colors**: Primary, background, foreground colors
- **Typography**: Heading and body font families
- **Spacing**: Tight, normal, or roomy spacing scales
- **Border Radius**: Consistent border radius values
- **Type Scale**: Small, medium, or large typography scales

### Environment Variables
- `GEMINI_API_KEY`: Your Google Gemini API key (required)

## 🔧 Development

### Project Structure
```
ai-website-generator/
├── app.py                 # Flask application
├── converter.py           # Prompt to spec conversion
├── website_generator.py   # Main website generation logic
├── component_templates.py # Component generation templates
├── schema.py             # Pydantic schemas
├── requirements.txt      # Python dependencies
├── setup.py             # Setup script
├── .env                 # Environment variables
└── templates/
    └── index.html       # Frontend template
```

### API Endpoints

- `GET /` - Frontend interface
- `POST /api/spec` - Generate website specification (JSON)
- `POST /api/generate` - Generate complete website (ZIP file)

### Adding New Components

1. Add the component type to `schema.py` in the `SectionType` literal
2. Add generation logic in `component_templates.py`
3. Add fallback template if needed

## 🐛 Troubleshooting

### Common Issues

**"GEMINI_API_KEY is missing" error**
- Make sure you've added your API key to the `.env` file
- Restart the Flask server after adding the key

**Components not generating properly**
- Check your internet connection
- Verify your Gemini API key is valid and has quota
- Try with a simpler prompt first

**Generated website won't start**
- Make sure you have Node.js installed
- Run `npm install` in the project directory
- Check for any error messages in the terminal

### Debug Mode
Run the Flask app in debug mode for detailed error messages:
```bash
export FLASK_DEBUG=1
python app.py
```

## 📝 Examples

### Example Prompts

**Portfolio Website**
```
Create a modern portfolio website for a UX designer with a clean, minimal design. 
Include a hero section, project gallery, about page, and contact form. 
Use a professional blue and white color scheme.
```

**Restaurant Website**
```
Build a restaurant website for an Italian bistro. Include a hero with food images, 
menu section, about us page, location/contact info, and reservation form. 
Use warm colors like red and gold.
```

**SaaS Landing Page**
```
Create a SaaS landing page for a project management tool. Include hero section, 
feature highlights, pricing plans, testimonials, and sign-up form. 
Use a modern tech aesthetic with blue and white colors.
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Google Gemini AI for intelligent code generation
- React team for the amazing framework
- Tailwind CSS for utility-first styling
- Vite team for the fast build tool

## 📞 Support

If you encounter any issues or have questions:

1. Check the troubleshooting section above
2. Search existing GitHub issues
3. Create a new issue with detailed information
4. Include your prompt, error messages, and system info

---

**Happy website generating! 🎉**