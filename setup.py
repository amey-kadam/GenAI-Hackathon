#!/usr/bin/env python3
"""
Improved Setup script for the Website Generator.

Usage:
    python setup.py          # interactive/default behavior
    python setup.py --yes    # auto accept prompts (installs requirements if requirements.txt exists)
    python setup.py --skip-install  # skip pip installs entirely
"""
from __future__ import annotations
import argparse
import os
import sys
import subprocess
from pathlib import Path

try:
    from dotenv import load_dotenv
except Exception:
    load_dotenv = None  # we'll warn later if needed

WELCOME = "🚀 Website Generator Setup"

def check_python_version(min_major=3, min_minor=8) -> bool:
    if sys.version_info < (min_major, min_minor):
        print(f"❌ Error: Python {min_major}.{min_minor}+ is required. Current: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def confirm(prompt: str) -> bool:
    resp = input(f"{prompt} [y/N]: ").strip().lower()
    return resp in ("y", "yes")

def install_requirements(requirements_path: Path, auto_confirm: bool) -> bool:
    if not requirements_path.exists():
        print(f"⚠️  No requirements file found at {requirements_path}")
        return True  # Not fatal — maybe project doesn't need Python deps

    if not auto_confirm:
        print(f"About to install Python requirements from {requirements_path}")
        if not confirm("Continue and run pip install -r requirements.txt?"):
            print("Skipping installation of requirements.")
            return True

    try:
        print("📦 Installing Python requirements...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", str(requirements_path)])
        print("✅ Python requirements installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print("❌ Error installing Python requirements:", e)
        return False

def ensure_env_file(env_path: Path) -> bool:
    """
    Ensure .env exists and has at least GEMINI_API_KEY placeholder.
    Returns True if GEMINI_API_KEY appears to be configured (non-placeholder).
    """
    created = False
    if not env_path.exists():
        print(f"⚠️  Creating {env_path} with example keys...")
        env_path.write_text(
            "# Example .env for Website Generator\n"
            "# Replace with your real keys before running the generator in production\n\n"
            "GEMINI_API_KEY=your_gemini_api_key_here\n"
            "OTHER_OPTION=example_value\n"
        )
        created = True
        print(f"✅ Created example {env_path}")

    if load_dotenv is None:
        print("⚠️  python-dotenv not installed. Can't load .env to validate values.")
        return not created  # if created just now, return False (needs user action)

    # load and check
    from dotenv import load_dotenv as _ld; _ld()
    from os import getenv
    api_key = getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_gemini_api_key_here":
        print("🔑 Please set GEMINI_API_KEY in the .env file (it currently looks missing or placeholder).")
        return False

    print("✅ Environment variables configured")
    return True

def ensure_templates_dir(base_dir: Path) -> None:
    templates_dir = base_dir / "templates"
    if not templates_dir.exists():
        templates_dir.mkdir(parents=True, exist_ok=True)
        print(f"✅ Created templates directory: {templates_dir}")
    else:
        print(f"✅ Templates directory exists: {templates_dir}")

def parse_args():
    p = argparse.ArgumentParser(description="Setup script for Website Generator")
    p.add_argument("--yes", action="store_true", help="Auto-confirm prompts (non-interactive)")
    p.add_argument("--skip-install", action="store_true", help="Skip pip installing requirements")
    return p.parse_args()

def main() -> int:
    args = parse_args()
    print(WELCOME)
    print("=" * len(WELCOME))

    ok = True

    if not check_python_version():
        ok = False

    base_dir = Path(__file__).resolve().parent
    requirements_path = base_dir / "requirements.txt"
    env_path = base_dir / ".env"

    if not args.skip_install:
        if not install_requirements(requirements_path, auto_confirm=args.yes):
            ok = False
    else:
        print("ℹ️  Skipping installation of Python requirements (per --skip-install)")

    env_ready = ensure_env_file(env_path)

    ensure_templates_dir(base_dir)

    print("\n" + "=" * len(WELCOME))
    if ok and env_ready:
        print("🎉 Setup completed successfully!")
        print("\nNext steps (example):")
        print("1. Add your GEMINI_API_KEY to the .env file.")
        print("2. Run your application or generator as documented (e.g. python run_generator.py or npm run dev for generated sites).")
        return 0
    else:
        if not ok:
            print("❌ Setup encountered errors. Please inspect messages above.")
        elif not env_ready:
            print("⚠️  Setup almost complete — please configure .env values (GEMINI_API_KEY).")
        return 1

if __name__ == "__main__":
    sys.exit(main())
