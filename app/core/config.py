from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # API Settings
    API_TITLE: str = "Resume Screening API"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "FastAPI application for resume screening using LlamaExtract"
    DEBUG: bool = False
    
    # LlamaExtract Settings
    LLAMA_CLOUD_API_KEY: str
    LLAMA_EXTRACT_AGENT_NAME: str = "resume-screening"
    LLAMA_EXTRACT_TIMEOUT: int = 300  # 5 minutes
    
    # File Upload Settings
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_FILE_EXTENSIONS: List[str] = [".pdf", ".docx", ".doc", ".txt"]
    UPLOAD_DIR: str = "uploads"
    
    # DigitalOcean Spaces (S3-compatible) Settings
    USE_SPACES: bool = False
    SPACES_ENDPOINT_URL: Optional[str] = None  # e.g., https://nyc3.digitaloceanspaces.com
    SPACES_REGION: Optional[str] = None        # e.g., nyc3
    SPACES_ACCESS_KEY_ID: Optional[str] = None
    SPACES_SECRET_ACCESS_KEY: Optional[str] = None
    SPACES_BUCKET_NAME: Optional[str] = None
    SPACES_KEY_PREFIX: str = ""              # optional folder/prefix
    SPACES_ACL: str = "public-read"          # or "private"
    SPACES_CDN_BASE_URL: Optional[str] = None # optional CDN base like https://cdn.example.com
    SPACES_DELETE_LOCAL_AFTER_UPLOAD: bool = False
    
    # CORS Settings
    # For development - specific origins
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:8000", "http://127.0.0.1:8000"]
    CORS_ALLOW_CREDENTIALS: bool = False
    CORS_ALLOW_METHODS: List[str] = ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]

    # Alternative: For production or multiple frontend URLs, uncomment below:
    # CORS_ORIGINS: List[str] = ["*"]  # But set CORS_ALLOW_CREDENTIALS to False
    # CORS_ALLOW_CREDENTIALS: bool = False
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 3600  # 1 hour
    
    # Background Tasks
    MAX_BACKGROUND_TASKS: int = 10
    TASK_TIMEOUT: int = 600  # 10 minutes
    
    # Database Settings (for storing job metadata)
    DATABASE_URL: Optional[str] = None
    USE_IN_MEMORY_DB: bool = True
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Screening Defaults
    DEFAULT_REQUIRED_SKILLS: List[str] = ["python", "machine learning", "data analysis"]
    DEFAULT_SCORING_WEIGHTS: dict = {
        "skills": 0.4,
        "experience": 0.3,
        "education": 0.2,
        "accomplishments": 0.1
    }
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings"""
    return settings


def setup_upload_directory():
    """Create upload directory if it doesn't exist"""
    upload_path = settings.UPLOAD_DIR
    if not os.path.exists(upload_path):
        os.makedirs(upload_path, exist_ok=True)
    return upload_path


def validate_settings():
    """Validate critical settings"""
    if not settings.LLAMA_CLOUD_API_KEY:
        raise ValueError("LLAMA_CLOUD_API_KEY environment variable is required")
    
    if settings.MAX_FILE_SIZE <= 0:
        raise ValueError("MAX_FILE_SIZE must be positive")
    
    if not settings.ALLOWED_FILE_EXTENSIONS:
        raise ValueError("ALLOWED_FILE_EXTENSIONS cannot be empty")
    
    return True
