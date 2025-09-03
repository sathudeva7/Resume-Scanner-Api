#!/bin/bash

echo "🚀 Resume Screening API Setup"
echo "============================"

# Check Python version
python_version=$(python3 --version 2>&1)
echo "📍 Using: $python_version"

# Create virtual environment
echo "🔧 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install --upgrade pip

# Try to install minimal requirements first
echo "   Installing minimal requirements..."
pip install -r requirements-minimal.txt

# Check if we can install python-magic (requires libmagic)
echo "   Checking for enhanced file type detection support..."
if command -v brew >/dev/null 2>&1; then
    echo "   Homebrew detected. You can install libmagic with: brew install libmagic"
elif command -v apt-get >/dev/null 2>&1; then
    echo "   APT detected. You can install libmagic with: sudo apt-get install libmagic1 libmagic-dev"
elif command -v yum >/dev/null 2>&1; then
    echo "   YUM detected. You can install libmagic with: sudo yum install file-devel"
fi

# Try to install python-magic
if pip install python-magic==0.4.27 >/dev/null 2>&1; then
    echo "   ✅ Enhanced file type detection enabled"
else
    echo "   ⚠️  Enhanced file type detection not available (libmagic not found)"
    echo "   📝 The app will work fine with basic file type detection"
    echo "   📖 See INSTALL.md for instructions to enable enhanced detection"
fi

# Create environment file
echo "⚙️  Setting up environment..."
if [ ! -f .env ]; then
    cp env.example .env
    echo "✅ Created .env file from template"
    echo "⚠️  Please edit .env and add your LLAMA_CLOUD_API_KEY"
else
    echo "✅ .env file already exists"
fi

# Create directories
echo "📁 Creating directories..."
mkdir -p uploads logs
echo "✅ Created uploads and logs directories"

# Make scripts executable
chmod +x run.py test_api.py

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file and add your LLAMA_CLOUD_API_KEY"
echo "2. Activate virtual environment: source venv/bin/activate"
echo "3. Start the API: python run.py"
echo "4. Test the API: python test_api.py"
echo ""
echo "📚 Documentation: http://localhost:8000/docs"
