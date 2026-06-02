"""
Automated setup script for Feynman Digital Twin
"""
import os
import sys
from pathlib import Path
import subprocess
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)


def setup_environment():
    """Setup Python environment and dependencies"""
    print("=" * 70)
    print("FEYNMAN DIGITAL TWIN - SETUP WIZARD")
    print("=" * 70)

    # Step 1: Check Python version
    print("\n[1/5] Checking Python version...")
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        sys.exit(1)
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor} detected")

    # Step 2: Install dependencies
    print("\n[2/5] Installing dependencies...")
    req_file = Path(__file__).parent / "requirements.txt"
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", str(req_file)])
        print("✓ Dependencies installed")
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        sys.exit(1)

    # Step 3: Setup .env file
    print("\n[3/5] Setting up environment variables...")
    env_file = Path(__file__).parent / ".env"
    env_template = Path(__file__).parent / ".env.template"

    if env_file.exists():
        print("  .env file already exists")
    else:
        if env_template.exists():
            with open(env_template, "r") as f:
                template_content = f.read()
            with open(env_file, "w") as f:
                f.write(template_content)
            print("✓ .env file created from template")
        else:
            print("❌ .env.template not found")

    # Ask for API key
    print("\n[4/5] API Configuration")
    print("  To use Feynman Twin, you need a Gemini API key from:")
    print("  https://aistudio.google.com/app/apikeys")

    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key:
        api_key = input("\n  Enter your GEMINI_API_KEY (or press Enter to set later): ").strip()

    if api_key:
        with open(env_file, "r") as f:
            content = f.read()
        content = content.replace("your_api_key_here", api_key)
        with open(env_file, "w") as f:
            f.write(content)
        print("✓ API key configured")
        os.environ["GEMINI_API_KEY"] = api_key
    else:
        print("  ⚠ Please update .env file with your API key later")

    # Step 5: Directory structure
    print("\n[5/5] Setting up directory structure...")
    directories = [
        Path(__file__).parent / "data" / "raw",
        Path(__file__).parent / "data" / "processed",
        Path(__file__).parent / "embeddings",
        Path(__file__).parent / "memory",
        Path(__file__).parent / "src",
    ]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

    print("✓ Directory structure ready")

    # Final instructions
    print("\n" + "=" * 70)
    print("✓ SETUP COMPLETE!")
    print("=" * 70)
    print("\nNext steps:")
    print("  1. cd src")
    print("  2. python main.py --setup    (collect data and build embeddings)")
    print("  3. python main.py            (start interactive session)")
    print("\nOr ask a single question:")
    print("  python main.py --query \"Your question here\"")
    print("\n" + "=" * 70)


def quick_start():
    """Quick start guide"""
    print("\n" + "=" * 70)
    print("QUICK START GUIDE")
    print("=" * 70)

    print("""
FEYNMAN DIGITAL TWIN - Talk with Richard Feynman's AI

1. SETUP (one-time)
   cd feynman_twin
   python setup.py setup
   # Follow the prompts to add your Gemini API key

2. INITIALIZE RAG (one-time)
   cd src
   python main.py --setup
   # This collects data and builds the knowledge base (~5-10 min)

3. START CHATTING
   python main.py
   # Start an interactive conversation
   
   OR ask a specific question:
   python main.py --query "Explain the double slit experiment"

COMMANDS IN INTERACTIVE MODE:
   - Type your question normally
   - 'memory' - See what I remember about you
   - 'save' - Manually save the session
   - 'quit' - Exit (session auto-saves)

EXAMPLE QUESTIONS:
   • What is the Feynman Technique?
   • Explain quantum mechanics simply
   • Why is curiosity important in science?
   • What's your approach to teaching?
   • How do you think about problem solving?
    """)
    print("=" * 70)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Feynman Twin Setup")
    parser.add_argument("command", nargs="?", default="setup")

    args = parser.parse_args()

    if args.command == "setup":
        setup_environment()
    elif args.command == "quickstart":
        quick_start()
    else:
        print("Unknown command. Use 'setup' or 'quickstart'")
