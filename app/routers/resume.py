import logging
from datetime import datetime
from typing import List, Optional
import uuid

from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks, Depends, Query
from fastapi.responses import HTMLResponse, JSONResponse

from app.models.api import (
    UploadResponse, ExtractionRequest, ExtractionResponse, JobStatusResponse,
    BatchScreeningRequest, BatchScreeningResponse, ResumeListResponse,
    BulkUploadResponse, ErrorResponse, TemplateGenerationRequest
)
from app.models.resume import ResumeExtractionJob, ScreeningCriteria, Resume
from app.services.extraction import get_extraction_service, LlamaExtractionService
from app.services.template_manager import get_template_manager, TemplateManager
from app.services.ai_adapter import get_ai_adapter_service, AiAdapterService
from app.utils.file_handler import get_file_handler, FileHandler
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["resume"])





@router.post("/upload-resume", response_model=UploadResponse)
async def upload_resume(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    file_handler: FileHandler = Depends(get_file_handler),
    extraction_service: LlamaExtractionService = Depends(get_extraction_service)
):
    """
    Upload a resume file for processing
    
    - **file**: Resume file (PDF, DOCX, DOC, TXT)
    - Returns job ID for tracking extraction progress
    """
    try:
        # Generate job ID
        job_id = str(uuid.uuid4())
        
        # Save uploaded file
        file_path, file_metadata = await file_handler.save_uploaded_file(file, job_id)
        
        # Create extraction job
        job_id = await extraction_service.create_extraction_job(file_path, file.filename)
        
        # Add background task for extraction
        background_tasks.add_task(
            extraction_service.extract_resume_data,
            job_id,
            file_path
        )
        
        return UploadResponse(
            job_id=job_id,
            filename=file.filename,
            file_size=file_metadata["file_size"],
            upload_time=datetime.utcnow(),
            status="PENDING",
            file_url=file_metadata.get("spaces_url") if getattr(settings, "USE_SPACES", False) else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.post("/extract-resume-data", response_model=ExtractionResponse)
async def extract_resume_data(
    request: ExtractionRequest,
    extraction_service: LlamaExtractionService = Depends(get_extraction_service)
):
    """
    Extract structured data from uploaded resume
    
    - **job_id**: Job ID from upload response
    - Returns extraction status and data if completed
    """
    try:
        job = await extraction_service.get_job_status(request.job_id)
        
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        if job.status == "SUCCESS":
            return ExtractionResponse(
                job_id=request.job_id,
                status=job.status,
                message="Extraction completed successfully",
                extracted_data=job.extracted_data
            )
        elif job.status == "ERROR":
            return ExtractionResponse(
                job_id=request.job_id,
                status=job.status,
                message="Extraction failed",
                error_details=job.error_message
            )
        else:
            return ExtractionResponse(
                job_id=request.job_id,
                status=job.status,
                message=f"Extraction is {job.status.lower()}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Extraction request failed: {e}")
        raise HTTPException(status_code=500, detail=f"Extraction request failed: {str(e)}")


@router.get("/resume/{job_id}", response_model=JobStatusResponse)
async def get_resume_status(
    job_id: str,
    extraction_service: LlamaExtractionService = Depends(get_extraction_service)
):
    """
    Get resume extraction job status
    
    - **job_id**: Job identifier
    - Returns job status and extracted data if available
    """
    try:
        job = await extraction_service.get_job_status(job_id)
        
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Calculate progress
        progress = None
        if job.status == "PENDING":
            progress = 0
        elif job.status == "PROCESSING":
            progress = 50
        elif job.status in ["SUCCESS", "ERROR"]:
            progress = 100
        
        return JobStatusResponse(
            job_id=job.job_id,
            filename=job.filename,
            status=job.status,
            created_at=job.created_at,
            completed_at=job.completed_at,
            progress=progress
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")


@router.get("/resume/{job_id}/data", response_model=Resume)
async def get_resume_data(
    job_id: str,
    extraction_service: LlamaExtractionService = Depends(get_extraction_service)
):
    """
    Get extracted resume data
    
    - **job_id**: Job identifier
    - Returns extracted structured data
    """
    try:
        job = await extraction_service.get_job_status(job_id)
        
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        if job.status != "SUCCESS":
            raise HTTPException(
                status_code=400,
                detail=f"Data not available. Job status: {job.status}"
            )
        
        if not job.extracted_data:
            raise HTTPException(status_code=404, detail="No extracted data available")
        
        return job.extracted_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Data retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=f"Data retrieval failed: {str(e)}")


@router.post("/screen-resumes", response_model=BatchScreeningResponse)
async def screen_resumes(
    request: BatchScreeningRequest,
    extraction_service: LlamaExtractionService = Depends(get_extraction_service)
):
    """
    Screen multiple resumes against job criteria
    
    - **job_ids**: List of job IDs to screen
    - **criteria**: Screening criteria (required skills, experience, etc.)
    - **include_unqualified**: Whether to include unqualified candidates
    """
    try:
        if not request.job_ids:
            raise HTTPException(status_code=400, detail="No job IDs provided")
        
        # Screen resumes
        results = await extraction_service.batch_screen_resumes(
            request.job_ids,
            request.criteria,
            request.include_unqualified
        )
        
        screening_id = str(uuid.uuid4())
        qualified_count = len([r for r in results if r.qualified])
        
        return BatchScreeningResponse(
            screening_id=screening_id,
            total_resumes=len(request.job_ids),
            qualified_count=qualified_count,
            results=results,
            screening_criteria=request.criteria,
            completed_at=datetime.utcnow()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Screening failed: {e}")
        raise HTTPException(status_code=500, detail=f"Screening failed: {str(e)}")


@router.get("/resumes", response_model=ResumeListResponse)
async def list_resumes(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    status: Optional[str] = Query(None, description="Filter by status"),
    extraction_service: LlamaExtractionService = Depends(get_extraction_service)
):
    """
    List all resume extraction jobs with pagination
    
    - **page**: Page number (starts from 1)
    - **page_size**: Number of items per page (max 100)
    - **status**: Filter by job status (optional)
    """
    try:
        offset = (page - 1) * page_size
        jobs = await extraction_service.list_jobs(limit=page_size + 1, offset=offset)
        
        # Filter by status if provided
        if status:
            jobs = [job for job in jobs if job.status.upper() == status.upper()]
        
        # Check if there are more pages
        has_more = len(jobs) > page_size
        if has_more:
            jobs = jobs[:page_size]
        
        total_count = len(jobs) + offset + (1 if has_more else 0)
        total_pages = (total_count + page_size - 1) // page_size
        
        return ResumeListResponse(
            total_count=total_count,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            resumes=jobs
        )
        
    except Exception as e:
        logger.error(f"List resumes failed: {e}")
        raise HTTPException(status_code=500, detail=f"List resumes failed: {str(e)}")


@router.post("/bulk-upload", response_model=BulkUploadResponse)
async def bulk_upload_resumes(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    file_handler: FileHandler = Depends(get_file_handler),
    extraction_service: LlamaExtractionService = Depends(get_extraction_service)
):
    """
    Upload multiple resume files for batch processing
    
    - **files**: List of resume files
    - Returns summary of upload results and job IDs
    """
    try:
        if len(files) > 50:  # Limit bulk uploads
            raise HTTPException(status_code=400, detail="Too many files. Maximum 50 files allowed.")
        
        job_ids = []
        errors = []
        successful_uploads = 0
        
        for file in files:
            try:
                # Generate job ID
                job_id = str(uuid.uuid4())
                
                # Save uploaded file
                file_path, file_metadata = await file_handler.save_uploaded_file(file, job_id)
                
                # Create extraction job
                job_id = await extraction_service.create_extraction_job(file_path, file.filename)
                job_ids.append(job_id)
                
                # Add background task for extraction
                background_tasks.add_task(
                    extraction_service.extract_resume_data,
                    job_id,
                    file_path
                )
                
                successful_uploads += 1
                
            except Exception as e:
                errors.append({
                    "filename": file.filename,
                    "error": str(e)
                })
        
        return BulkUploadResponse(
            total_files=len(files),
            successful_uploads=successful_uploads,
            failed_uploads=len(errors),
            job_ids=job_ids,
            errors=errors
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Bulk upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Bulk upload failed: {str(e)}")


@router.post("/create-template/{job_id}", response_class=HTMLResponse)
async def create_resume_template(
    job_id: str,
    request: TemplateGenerationRequest,
    extraction_service: LlamaExtractionService = Depends(get_extraction_service),
    template_manager: TemplateManager = Depends(get_template_manager),
    ai_adapter: AiAdapterService = Depends(get_ai_adapter_service)
):
    """
    Generate HTML resume template for a completed extraction job

    - **job_id**: Job identifier from upload response
    - **request**: Template generation request containing template_id and optional job_description
      - **template_id**: Template to use (1=Modern gradient template, 2=Clean Tailwind template, 3=Modern CV with sidebar)
      - **job_description**: Optional job description to tailor the resume content to the specific role using AI
    - Returns HTML template populated with candidate data (optionally AI-tailored)
    """
    try:
        # Get job status
        job = await extraction_service.get_job_status(job_id)

        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        if job.status != "SUCCESS":
            raise HTTPException(
                status_code=400,
                detail=f"Resume data not available. Job status: {job.status}"
            )

        if not job.extracted_data:
            raise HTTPException(status_code=404, detail="No extracted data available")

        # Convert Resume model to dictionary for template generation
        candidate_data = {
            "name": job.extracted_data.name,
            "email": job.extracted_data.email,
            "links": job.extracted_data.links,
            "experience": [
                {
                    "company": exp.company,
                    "title": exp.title,
                    "description": exp.description,
                    "start_date": exp.start_date,
                    "end_date": exp.end_date,
                    "dates": f"{exp.start_date} - {exp.end_date if exp.end_date else 'Present'}"
                } for exp in job.extracted_data.experience
            ],
            "education": [
                {
                    "institution": edu.institution,
                    "degree": edu.degree,
                    "start_date": edu.start_date,
                    "end_date": edu.end_date,
                    "dates": f"{edu.start_date} - {edu.end_date if edu.end_date else 'Present'}",
                    "gpa": f"Major: {edu.degree}" if hasattr(edu, 'degree') and edu.degree else ""
                } for edu in job.extracted_data.education
            ],
            "technical_skills": {
                "programming_languages": job.extracted_data.technical_skills.programming_languages,
                "frameworks": job.extracted_data.technical_skills.frameworks,
                "skills": job.extracted_data.technical_skills.skills
            },
            "key_accomplishments": job.extracted_data.key_accomplishments,
            # Add additional fields that templates might need
            "title": getattr(job.extracted_data, "title", None) or "Professional",
            "location": getattr(job.extracted_data, "location", None) or "City, Country",
            "phone": getattr(job.extracted_data, "phone", None) or "+00 0000 000000",
            "portfolio_url": getattr(job.extracted_data, "portfolio_url", None) or "#",
            "github_url": getattr(job.extracted_data, "github_url", None) or "#",
            "languages": getattr(job.extracted_data, "languages", None) or []
        }

        # Apply AI tailoring if job description is provided
        if request.job_description and request.job_description.strip():
            logger.info(f"Applying AI tailoring for job_id: {job_id}")
            try:
                candidate_data = ai_adapter.tailor_candidate(candidate_data, request.job_description)
                logger.info("AI tailoring completed successfully")
            except Exception as e:
                logger.warning(f"AI tailoring failed, using original data: {e}")
        else:
            logger.info("No job description provided, skipping AI tailoring")

        # Generate HTML template using template manager
        html_content = template_manager.get_template(request.template_id, candidate_data)

        return HTMLResponse(content=html_content, status_code=200)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Template generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Template generation failed: {str(e)}")


@router.get("/templates", response_model=dict[int, str])
async def get_available_templates(
    template_manager: TemplateManager = Depends(get_template_manager)
):
    """
    Get list of available resume templates

    Returns a dictionary mapping template IDs to their descriptions
    """
    try:
        return template_manager.get_available_templates()
    except Exception as e:
        logger.error(f"Failed to get templates: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get templates: {str(e)}")


@router.get("/ai-adapter/status")
async def get_ai_adapter_status(
    ai_adapter: AiAdapterService = Depends(get_ai_adapter_service)
):
    """
    Get AI adapter service status and configuration
    
    Returns information about OpenAI integration availability
    """
    try:
        status = ai_adapter.get_status()
        return {
            "ai_tailoring_available": ai_adapter.is_available(),
            "status": status,
            "message": "AI tailoring ready" if ai_adapter.is_available() else "AI tailoring not available"
        }
    except Exception as e:
        logger.error(f"Failed to get AI adapter status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get AI adapter status: {str(e)}")


@router.delete("/resume/{job_id}")
async def delete_resume(
    job_id: str,
    extraction_service: LlamaExtractionService = Depends(get_extraction_service),
    file_handler: FileHandler = Depends(get_file_handler)
):
    """
    Delete a resume and its associated data

    - **job_id**: Job identifier
    """
    try:
        # Get job to find file path
        job = await extraction_service.get_job_status(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        # Delete job from service
        deleted = await extraction_service.delete_job(job_id)

        # Try to delete associated file and Spaces object (if enabled)
        try:
            from pathlib import Path
            file_ext = Path(job.filename).suffix.lower()
            saved_filename = f"{job_id}{file_ext}"
            file_path = Path(settings.UPLOAD_DIR) / saved_filename
            file_handler.delete_file(file_path)
            # Attempt Spaces deletion when enabled
            if getattr(settings, "USE_SPACES", False):
                try:
                    file_handler.delete_spaces_object(saved_filename)
                except Exception as e:
                    logger.warning(f"Could not delete Spaces object for job {job_id}: {e}")
        except Exception as e:
            logger.warning(f"Could not delete file for job {job_id}: {e}")

        if deleted:
            return {"message": f"Resume {job_id} deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Job not found")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete failed: {e}")
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")
