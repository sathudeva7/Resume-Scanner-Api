import logging
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi

from app.core.config import settings, validate_settings, setup_upload_directory
from app.routers import resume
from app.services.extraction import get_extraction_service
from app.models.api import HealthResponse, ErrorResponse
from app.db.database import engine, Base



# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format=settings.LOG_FORMAT
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting Resume Screening API...")
    
    try:
        # Validate settings
        validate_settings()
        logger.info("Settings validated successfully")
        
        # Setup upload directory
        setup_upload_directory()
        logger.info(f"Upload directory setup: {settings.UPLOAD_DIR}")
        
        # Initialize database if configured
        try:
            if settings.DATABASE_URL:
                async with engine.begin() as conn:
                    await conn.run_sync(Base.metadata.create_all)
                logger.info("Database initialized successfully")
            else:
                logger.info("Database not configured or in-memory mode enabled; skipping DB init")
        except Exception as db_e:
            logger.error(f"Database initialization failed: {db_e}")
            raise

        # Initialize extraction service
        extraction_service = await get_extraction_service()
        logger.info("LlamaExtract service initialized")
        
        logger.info("Application startup completed successfully")
        
    except Exception as e:
        logger.error(f"Startup failed: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Resume Screening API...")


# Create FastAPI application
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description=settings.API_DESCRIPTION,
    lifespan=lifespan,
    debug=settings.DEBUG
)

# Add CORS middleware
origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:5173",
    "https://capable-pika-72db40.netlify.app/*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Include routers
app.include_router(resume.router)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint
    
    Returns the current status of the API and its dependencies
    """
    try:
        # Check LlamaExtract service
        extraction_service = await get_extraction_service()
        llama_status = await extraction_service.health_check()
        
        # Build response
        dependencies = {
            "llama_extract": llama_status.get("status", "unknown"),
            "file_system": "healthy" if setup_upload_directory() else "unhealthy"
        }
        
        overall_status = "healthy" if all(
            status in ["healthy", "ok"] for status in dependencies.values()
        ) else "degraded"
        
        return HealthResponse(
            status=overall_status,
            timestamp=datetime.utcnow(),
            version=settings.API_VERSION,
            llama_extract_status=llama_status.get("status", "unknown"),
            dependencies=dependencies
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            status="unhealthy",
            timestamp=datetime.utcnow(),
            version=settings.API_VERSION,
            llama_extract_status="error",
            dependencies={"error": str(e)}
        )


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Resume Screening API",
        "version": settings.API_VERSION,
        "description": "FastAPI application for resume screening using LlamaExtract",
        "docs_url": "/docs",
        "health_url": "/health",
        "status": "online"
    }


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=f"HTTP {exc.status_code}",
            message=exc.detail,
            timestamp=datetime.utcnow()
        ).model_dump()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    """General exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal Server Error",
            message="An unexpected error occurred",
            details={"exception": str(exc)} if settings.DEBUG else None,
            timestamp=datetime.utcnow()
        ).model_dump()
    )


def custom_openapi():
    """Custom OpenAPI schema with enhanced documentation"""
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=settings.API_TITLE,
        version=settings.API_VERSION,
        description=f"""
        {settings.API_DESCRIPTION}
        
        ## Features
        
        * **Resume Upload**: Upload PDF, DOCX, DOC, and TXT files
        * **Data Extraction**: Extract structured data using LlamaExtract
        * **Resume Screening**: Screen candidates against job criteria
        * **Batch Processing**: Handle multiple resumes simultaneously
        * **Real-time Status**: Track job progress and status
        
        ## Authentication
        
        This API requires a valid LlamaCloud API key configured on the server.
        
        ## Rate Limiting
        
        Requests are limited to {settings.RATE_LIMIT_REQUESTS} per {settings.RATE_LIMIT_WINDOW} seconds.
        
        ## File Limits
        
        * Maximum file size: {settings.MAX_FILE_SIZE // (1024*1024)}MB
        * Supported formats: {', '.join(settings.ALLOWED_FILE_EXTENSIONS)}
        * Bulk upload limit: 50 files
        """,
        routes=app.routes,
    )
    
    # Add security scheme if needed
    openapi_schema["info"]["x-logo"] = {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
