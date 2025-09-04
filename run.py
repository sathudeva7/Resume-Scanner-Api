#!/usr/bin/env python3
"""
Resume Screening API runner script
"""

import os
import sys
import subprocess
from pathlib import Path

def check_requirements():
    """Check if requirements are installed"""
    try:
        import fastapi
        import uvicorn
        import pydantic
        print("✅ Basic requirements found")
        
        # Check for optional dependencies
        try:
            import magic
            print("✅ Enhanced file type detection available")
        except ImportError:
            print("ℹ️  Enhanced file type detection not available (using fallback)")
            print("   Install libmagic and python-magic for better file detection")
        
        return True
    except ImportError as e:
        print(f"❌ Missing requirements: {e}")
        print("Please install requirements: pip install -r requirements-minimal.txt")
        return False

def check_environment():
    """Check environment configuration"""
    required_vars = ["LLAMA_CLOUD_API_KEY"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Please set these in your .env file or environment")
        return False
    
    print("✅ Environment configuration looks good")
    return True

def setup_directories():
    """Create necessary directories"""
    directories = ["uploads", "logs"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    print("✅ Directories created")

def main():
    """Main runner function"""
    print("🚀 Resume Screening API")
    print("=" * 30)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Check environment
    if not check_environment():
        print("\nTo set up environment:")
        print("1. Copy env.example to .env")
        print("2. Add your LLAMA_CLOUD_API_KEY")
        print("3. Run this script again")
        print("\nAlternatively, set environment variable:")
        print("export LLAMA_CLOUD_API_KEY=your_api_key_here")
        
        # Ask if user wants to continue without API key (for testing)
        response = input("\nContinue without API key? (y/N): ").lower().strip()
        if response != 'y':
            sys.exit(1)
        else:
            print("⚠️  Running without API key - some features may not work")
    
    # Setup directories
    setup_directories()
    
    # Start the application
    print("\n🌟 Starting the API server...")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🔍 Health Check: http://localhost:8000/health")
    print("🛑 Press Ctrl+C to stop\n")
    
    try:
        # Run uvicorn
        cmd = [
            sys.executable, "-m", "uvicorn",
            "app.main:app",
            "--host", "0.0.0.0",
            "--port", "8080",
            "--reload"
        ]
        
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
