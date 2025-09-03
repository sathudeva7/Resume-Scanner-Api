from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from .resume import Resume, ResumeExtractionJob, ScreeningCriteria, ScreeningResult


class UploadResponse(BaseModel):
    """Response for file upload"""
    job_id: str = Field(description="Unique job identifier for tracking")
    filename: str = Field(description="Original filename")
    file_size: int = Field(description="File size in bytes")
    upload_time: datetime = Field(description="Upload timestamp")
    status: str = Field(description="Initial status (usually PENDING)")
    file_url: Optional[str] = Field(default=None, description="Public URL if stored in Spaces")


class ExtractionRequest(BaseModel):
    """Request to extract data from uploaded resume"""
    job_id: str = Field(description="Job ID from upload response")


class ExtractionResponse(BaseModel):
    """Response for extraction request"""
    job_id: str = Field(description="Job identifier")
    status: str = Field(description="Extraction status")
    message: str = Field(description="Status message")
    extracted_data: Optional[Resume] = Field(default=None, description="Extracted resume data if completed")
    error_details: Optional[str] = Field(default=None, description="Error details if failed")


class JobStatusResponse(BaseModel):
    """Response for job status check"""
    job_id: str = Field(description="Job identifier")
    filename: str = Field(description="Original filename")
    status: str = Field(description="Current job status")
    created_at: datetime = Field(description="Job creation time")
    completed_at: Optional[datetime] = Field(default=None, description="Job completion time")
    progress: Optional[int] = Field(default=None, description="Progress percentage (0-100)")
    estimated_completion: Optional[datetime] = Field(default=None, description="Estimated completion time")


class BatchScreeningRequest(BaseModel):
    """Request for batch resume screening"""
    job_ids: List[str] = Field(description="List of job IDs to screen")
    criteria: ScreeningCriteria = Field(description="Screening criteria")
    include_unqualified: bool = Field(
        default=False,
        description="Whether to include unqualified candidates in results"
    )


class BatchScreeningResponse(BaseModel):
    """Response for batch screening"""
    screening_id: str = Field(description="Unique screening identifier")
    total_resumes: int = Field(description="Total number of resumes screened")
    qualified_count: int = Field(description="Number of qualified candidates")
    results: List[ScreeningResult] = Field(description="Screening results sorted by score")
    screening_criteria: ScreeningCriteria = Field(description="Criteria used for screening")
    completed_at: datetime = Field(description="Screening completion time")


class ErrorResponse(BaseModel):
    """Standard error response"""
    error: str = Field(description="Error type")
    message: str = Field(description="Error message")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Additional error details")
    timestamp: datetime = Field(description="Error timestamp")


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(description="Service status")
    timestamp: datetime = Field(description="Health check timestamp")
    version: str = Field(description="API version")
    llama_extract_status: str = Field(description="LlamaExtract service status")
    dependencies: Dict[str, str] = Field(description="Dependency status")


class FileValidationResponse(BaseModel):
    """File validation response"""
    valid: bool = Field(description="Whether file is valid")
    file_type: str = Field(description="Detected file type")
    file_size: int = Field(description="File size in bytes")
    issues: List[str] = Field(default_factory=list, description="Validation issues if any")


class ResumeListResponse(BaseModel):
    """Response for listing resumes"""
    total_count: int = Field(description="Total number of resumes")
    page: int = Field(description="Current page number")
    page_size: int = Field(description="Number of items per page")
    total_pages: int = Field(description="Total number of pages")
    resumes: List[ResumeExtractionJob] = Field(description="List of resume jobs")


class BulkUploadResponse(BaseModel):
    """Response for bulk file upload"""
    total_files: int = Field(description="Total number of files uploaded")
    successful_uploads: int = Field(description="Number of successful uploads")
    failed_uploads: int = Field(description="Number of failed uploads")
    job_ids: List[str] = Field(description="List of created job IDs")
    errors: List[Dict[str, str]] = Field(
        default_factory=list,
        description="List of errors for failed uploads"
    )


class AgentInfo(BaseModel):
    """LlamaExtract agent information"""
    agent_id: str = Field(description="Agent identifier")
    name: str = Field(description="Agent name")
    schema_version: str = Field(description="Current schema version")
    created_at: datetime = Field(description="Agent creation time")
    last_updated: datetime = Field(description="Last schema update time")
    total_extractions: int = Field(description="Total number of extractions performed")
