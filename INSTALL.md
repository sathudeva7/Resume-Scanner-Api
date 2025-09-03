# Installation Guide

## Quick Start (Minimal Dependencies)

For basic functionality without enhanced file type detection:

```bash
# 1. Install minimal Python dependencies
pip install -r requirements-minimal.txt

# 2. Set up environment
cp env.example .env
# Edit .env and add your LLAMA_CLOUD_API_KEY

# 3. Run the application
python run.py
```

## Full Installation (with Enhanced File Type Detection)

For enhanced file type detection capabilities, you'll need to install the system `libmagic` library and the `python-magic` package.

### macOS

```bash
# Install libmagic using Homebrew
brew install libmagic

# Install Python dependencies with magic support
pip install -r requirements.txt
```

### Ubuntu/Debian

```bash
# Install libmagic system library
sudo apt-get update
sudo apt-get install libmagic1 libmagic-dev

# Install Python dependencies with magic support
pip install -r requirements.txt
```

### CentOS/RHEL/Fedora

```bash
# Install libmagic system library
sudo yum install file-devel  # CentOS/RHEL
# OR
sudo dnf install file-devel  # Fedora

# Install Python dependencies with magic support
pip install -r requirements.txt
```

### Windows

```bash
# Install python-magic-bin (includes libmagic for Windows)
pip install python-magic-bin

# Then install other requirements
pip install -r requirements.txt
```

### Docker (Recommended for Production)

The easiest way to get all dependencies:

```bash
# Build and run with Docker (includes all system dependencies)
docker build -t resume-api .
docker run -p 8000:8000 -e LLAMA_CLOUD_API_KEY=your_key resume-api

# OR use docker-compose
docker-compose up
```

## Troubleshooting

### libmagic Issues

If you encounter `ImportError: failed to find libmagic`, the application will automatically fall back to extension-based file type detection. This is sufficient for most use cases.

To enable enhanced file type detection:

1. **macOS**: `brew install libmagic`
2. **Ubuntu**: `sudo apt-get install libmagic1 libmagic-dev`
3. **Windows**: `pip install python-magic-bin`
4. Then: `pip install python-magic==0.4.27`

### Alternative: Use Docker

The Docker image includes all system dependencies and is the recommended way to avoid system dependency issues:

```bash
# Quick Docker run
docker run -p 8000:8000 -e LLAMA_CLOUD_API_KEY=your_key resume-api
```

### Environment Variables

Make sure to set your LlamaCloud API key:

```bash
# Option 1: Environment variable
export LLAMA_CLOUD_API_KEY=your_api_key_here

# Option 2: .env file
echo "LLAMA_CLOUD_API_KEY=your_api_key_here" > .env
```

### Testing Installation

```bash
# Test the installation
python test_api.py

# Or check health endpoint
curl http://localhost:8000/health
```

## Development Setup

For development with all tools:

```bash
# Install development dependencies
pip install -r requirements.txt

# Install pre-commit hooks (optional)
pre-commit install

# Run tests
pytest

# Format code
black app/
isort app/
```
