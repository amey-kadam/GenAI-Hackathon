#!/usr/bin/env python3
"""
Setup script for the Website Generator
"""
import os
import sys
import subprocess

def check_python_version():
    """Check if Python version is 3.8+"""
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def install_requirements():
    """Install Python requirements"""
    try:
        print("📦 Installing Python requirements...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Python requirements installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Error installing Python requirements")
        return False

def check_env_file():
    """Check if .env file exists and has required variables"""
    if not os.path.exists('.env'):
        print("⚠️  Creating .env file...")
        with open('.env', 'w') as f:
            f.write("# Add your Gemini API key here\n")
            f.write("GEMINI_API_KEY=your_gemini_api_key_here\n")
        print("✅ .env file created")
        print("🔑 Please add your Gemini API key to the .env file")
        return False
    
    # Check if API key is set
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key or api_key == 'your_gemini_api_key_here':
        print("🔑 Please set your GEMINI_API_KEY in the .env file")
        return False
    
    print("✅ Environment variables configured")
    return True

def create_templates_dir():
    """Create templates directory if it doesn't exist"""
    templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
    if not os.path.exists(templates_dir):
        os.makedirs(templates_dir)
        print("✅ Templates directory created")
    return True

def main():
    print("🚀 Website Generator Setup")
    print("=" * 30)
    
    success = True
    
    # Check Python version
    if not check_python_version():
        success = False
    
    # Install requirements
    if success and not install_requirements():
        success = False
    
    # Check environment file
    env_configured = check_env_file()
    
    # Create templates directory
    if success:
        create_templates_dir()
    
    print("\n" + "=" * 30)
    if success and env_configured:
        print("🎉 Setup completed successfully!")
        print("\nNext steps:")
        print("1. Run: python app.py")
        print("2. Open: http://localhost:5000")
        print("3. Start generating websites!")
    elif success:
        print("⚠️  Setup almost complete!")
        print("Please configure your Gemini API key in the .env file")
        print("Then run: python app.py")
    else:
        print("❌ Setup failed. Please check the errors above.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())