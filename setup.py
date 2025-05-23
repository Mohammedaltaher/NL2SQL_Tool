"""
Quick setup script for NL2SQL Tool
This script helps you get started quickly with the NL2SQL Tool
"""

import os
import subprocess
import sys
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors"""
    print(f"📋 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return False


def check_python():
    """Check Python version"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")
    return True


def check_ollama():
    """Check if Ollama is installed"""
    try:
        result = subprocess.run("ollama --version", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Ollama is installed")
            return True
    except:
        pass
    
    print("❌ Ollama not found. Please install Ollama from https://ollama.ai")
    return False


def setup_virtual_environment():
    """Set up Python virtual environment"""
    if os.path.exists("venv"):
        print("✅ Virtual environment already exists")
        return True
    
    return run_command("python -m venv venv", "Creating virtual environment")


def install_requirements():
    """Install Python requirements"""
    # Check if we're in a virtual environment
    activate_script = "venv\\Scripts\\Activate.ps1" if os.name == 'nt' else "venv/bin/activate"
    
    if os.name == 'nt':  # Windows
        command = f"venv\\Scripts\\python.exe -m pip install -r requirements.txt"
    else:  # Unix/Linux/macOS
        command = f"venv/bin/python -m pip install -r requirements.txt"
    
    return run_command(command, "Installing Python requirements")


def setup_ollama_model():
    """Set up Ollama model"""
    print("🤖 Setting up Ollama model...")
    
    # Check if ollama serve is running
    try:
        subprocess.run("ollama list", shell=True, check=True, capture_output=True)
    except subprocess.CalledProcessError:
        print("📋 Starting Ollama service...")
        # Start Ollama service in background
        if os.name == 'nt':  # Windows
            subprocess.Popen("ollama serve", shell=True)
        else:
            subprocess.Popen(["ollama", "serve"])
        
        import time
        time.sleep(3)  # Wait for service to start
    
    # Pull the model
    return run_command("ollama pull llama2", "Downloading Llama2 model (this may take a while)")


def create_sample_database():
    """Create sample database"""
    print("📊 Creating sample database...")
    
    # Create data directory if it doesn't exist
    os.makedirs("data", exist_ok=True)
    
    # The sample database will be created automatically when the app starts
    print("✅ Sample database will be created automatically")
    return True


def main():
    """Main setup function"""
    print("🚀 NL2SQL Tool Setup")
    print("=" * 50)
    
    # Check prerequisites
    if not check_python():
        return False
    
    if not check_ollama():
        print("\n📝 Please install Ollama first:")
        print("1. Visit https://ollama.ai")
        print("2. Download and install Ollama")
        print("3. Run this setup script again")
        return False
    
    # Setup steps
    steps = [
        ("Virtual Environment", setup_virtual_environment),
        ("Python Requirements", install_requirements),
        ("Sample Database", create_sample_database),
        ("Ollama Model", setup_ollama_model),
    ]
    
    for step_name, step_function in steps:
        print(f"\n📋 Setting up {step_name}...")
        if not step_function():
            print(f"❌ Failed to set up {step_name}")
            return False
    
    print("\n" + "=" * 50)
    print("🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Activate virtual environment:")
    if os.name == 'nt':  # Windows
        print("   .\\venv\\Scripts\\Activate.ps1")
    else:
        print("   source venv/bin/activate")
    
    print("2. Start the application:")
    print("   python main.py")
    
    print("3. Open your browser to:")
    print("   http://localhost:8000")
    
    print("\n📚 For more information, see README.md")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
