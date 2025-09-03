# Resume Screening API

A production-ready FastAPI application for intelligent resume screening using LlamaExtract from LlamaCloud. This service extracts structured data from resume files and provides comprehensive candidate screening capabilities.

## 🚀 Features

- **Resume Upload & Processing**: Upload PDF, DOCX, DOC, and TXT files
- **Data Extraction**: Extract structured data using LlamaExtract AI
- **Smart Screening**: Screen candidates against job criteria with scoring
- **Batch Processing**: Handle multiple resumes simultaneously
- **Real-time Tracking**: Monitor job progress and status
- **RESTful API**: Clean, well-documented REST endpoints
- **Production Ready**: CORS, error handling, logging, and validation

## 📋 Requirements

- Python 3.8+
- LlamaCloud API Key
- FastAPI and dependencies (see requirements.txt)

## 🛠️ Installation

### 1. Clone and Setup

```bash
git clone <your-repo>
cd fastapi_resume_scoring
```

### 2. Install Dependencies

#### Option A: Quick Start (Basic File Detection)
```bash
# Install minimal dependencies (works without system libraries)
pip install -r requirements-minimal.txt
```

#### Option B: Full Installation (Enhanced File Detection)
For better file type detection, install system dependencies first:

**macOS:**
```bash
brew install libmagic
pip install -r requirements.txt
```

**Ubuntu/Debian:**
```bash
sudo apt-get install libmagic1 libmagic-dev
pip install -r requirements.txt
```

**Windows:**
```bash
pip install python-magic-bin
pip install -r requirements.txt
```

#### Option C: Docker (Recommended)
```bash
# No system dependencies needed - everything included
docker-compose up
```

### 3. Environment Configuration

```bash
# Copy example environment file
cp env.example .env

# Edit .env file with your settings
nano .env
```

Required environment variables:
```env
LLAMA_CLOUD_API_KEY=your_llama_cloud_api_key_here
```

### 4. Run the Application

```bash
# Development mode
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 📚 API Documentation

Once running, visit:
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 🔄 API Endpoints

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/upload-resume` | Upload resume file |
| POST | `/api/v1/extract-resume-data` | Extract data from resume |
| GET | `/api/v1/resume/{job_id}` | Get job status |
| GET | `/api/v1/resume/{job_id}/data` | Get extracted data |
| POST | `/api/v1/screen-resumes` | Screen multiple resumes |
| GET | `/api/v1/resumes` | List all resumes |
| POST | `/api/v1/bulk-upload` | Upload multiple files |
| DELETE | `/api/v1/resume/{job_id}` | Delete resume |

### Utility Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/` | API information |

## 💡 Usage Examples

### 1. Upload a Resume

```bash
curl -X POST "http://localhost:8000/api/v1/upload-resume" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@resume.pdf"
```

Response:
```json
{
  "job_id": "123e4567-e89b-12d3-a456-426614174000",
  "filename": "resume.pdf",
  "file_size": 245760,
  "upload_time": "2024-01-15T10:30:00Z",
  "status": "PENDING"
}
```

### 2. Check Job Status

```bash
curl "http://localhost:8000/api/v1/resume/123e4567-e89b-12d3-a456-426614174000"
```

### 3. Get Extracted Data

```bash
curl "http://localhost:8000/api/v1/resume/123e4567-e89b-12d3-a456-426614174000/data"
```

### 4. Screen Resumes

```bash
curl -X POST "http://localhost:8000/api/v1/screen-resumes" \
  -H "Content-Type: application/json" \
  -d '{
    "job_ids": ["job-id-1", "job-id-2"],
    "criteria": {
      "required_skills": ["Python", "Machine Learning"],
      "preferred_skills": ["FastAPI", "Docker"],
      "min_years_experience": 3
    },
    "include_unqualified": false
  }'
```

### 5. Bulk Upload

```bash
curl -X POST "http://localhost:8000/api/v1/bulk-upload" \
  -H "Content-Type: multipart/form-data" \
  -F "files=@resume1.pdf" \
  -F "files=@resume2.docx" \
  -F "files=@resume3.txt"
```

## 🐍 Python Client Example

```python
import requests
import json

# Upload resume
def upload_resume(file_path):
    with open(file_path, 'rb') as f:
        response = requests.post(
            "http://localhost:8000/api/v1/upload-resume",
            files={"file": f}
        )
    return response.json()

# Screen resumes
def screen_resumes(job_ids, criteria):
    response = requests.post(
        "http://localhost:8000/api/v1/screen-resumes",
        json={
            "job_ids": job_ids,
            "criteria": criteria,
            "include_unqualified": False
        }
    )
    return response.json()

# Example usage
job_response = upload_resume("resume.pdf")
job_id = job_response["job_id"]

# Wait for processing...
import time
time.sleep(10)

# Screen the resume
screening_criteria = {
    "required_skills": ["Python", "FastAPI", "Machine Learning"],
    "preferred_skills": ["Docker", "AWS"],
    "min_years_experience": 2
}

results = screen_resumes([job_id], screening_criteria)
print(json.dumps(results, indent=2))
```

## 📊 Data Models

### Resume Schema
```python
{
  "name": "John Doe",
  "email": "john@example.com",
  "links": ["linkedin.com/in/johndoe"],
  "experience": [
    {
      "company": "Tech Corp",
      "title": "Software Engineer",
      "description": "Built web applications...",
      "start_date": "2020",
      "end_date": "2023"
    }
  ],
  "education": [
    {
      "institution": "University",
      "degree": "Bachelor of Science",
      "start_date": "2016",
      "end_date": "2020"
    }
  ],
  "technical_skills": {
    "programming_languages": ["Python", "JavaScript"],
    "frameworks": ["FastAPI", "React"],
    "skills": ["Machine Learning", "Data Analysis"]
  },
  "key_accomplishments": "Led development of..."
}
```

### Screening Criteria
```python
{
  "required_skills": ["Python", "Machine Learning"],
  "preferred_skills": ["FastAPI", "Docker"],
  "min_years_experience": 3,
  "required_education_level": "Bachelor",
  "keywords": ["AI", "automation"]
}
```

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `LLAMA_CLOUD_API_KEY` | LlamaCloud API key | Required |
| `LLAMA_EXTRACT_AGENT_NAME` | Agent name for extractions | "resume-screening-api" |
| `MAX_FILE_SIZE` | Maximum file size in bytes | 10485760 (10MB) |
| `UPLOAD_DIR` | Upload directory | "uploads" |
| `LOG_LEVEL` | Logging level | "INFO" |
| `DEBUG` | Debug mode | false |

### File Support

- **PDF**: Adobe PDF files
- **DOCX**: Microsoft Word (newer format)
- **DOC**: Microsoft Word (legacy format)
- **TXT**: Plain text files

Maximum file size: 10MB (configurable)

## 🚀 Deployment

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements-minimal.txt .
RUN pip install -r requirements-minimal.txt

COPY app/ ./app/
COPY env.example .env

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t resume-screening-api .
docker run -p 8000:8000 -e LLAMA_CLOUD_API_KEY=your_key resume-screening-api
```

### Production Deployment

```bash
# Install dependencies
pip install -r requirements-minimal.txt

# Set environment variables
export LLAMA_CLOUD_API_KEY=your_key
export DEBUG=false
export LOG_LEVEL=WARNING

# Run with Gunicorn
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## 🧪 Testing

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest

# Run with coverage
pytest --cov=app tests/
```

## 🐛 Troubleshooting

### Common Issues

1. **LlamaCloud API Key Error**
   ```
   Error: LLAMA_CLOUD_API_KEY environment variable is required
   ```
   Solution: Set your LlamaCloud API key in environment variables

2. **File Upload Fails**
   ```
   Error: File size exceeds maximum allowed size
   ```
   Solution: Check file size limits in configuration

3. **Extraction Timeout**
   ```
   Error: Extraction timed out
   ```
   Solution: Increase `LLAMA_EXTRACT_TIMEOUT` setting

### Logs

Check application logs for detailed error information:
```bash
tail -f logs/app.log
```

## 📝 Development

### Project Structure
```
app/
├── main.py              # FastAPI application
├── models/
│   ├── resume.py        # Resume Pydantic models
│   └── api.py          # API request/response models
├── services/
│   └── extraction.py    # LlamaExtract service logic
├── routers/
│   └── resume.py       # Resume-related endpoints
├── core/
│   └── config.py       # Configuration and settings
└── utils/
    └── file_handler.py  # File processing utilities
```

### Adding New Features

1. Define models in `app/models/`
2. Implement service logic in `app/services/`
3. Add endpoints in `app/routers/`
4. Update configuration in `app/core/config.py`

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📞 Support

For issues and questions:
- Create an issue on GitHub
- Check the API documentation at `/docs`
- Review logs for error details