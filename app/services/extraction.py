import asyncio
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List
from pathlib import Path
import uuid

from llama_cloud_services import LlamaExtract
from llama_cloud.core.api_error import ApiError
from pydantic import ValidationError

from app.core.config import settings
from app.models.resume import Resume, ResumeExtractionJob, ScreeningCriteria, ScreeningResult
from app.models.api import JobStatusResponse
from app.db.database import async_session_maker
from app.db.repositories import ResumeJobRepository


logger = logging.getLogger(__name__)


class LlamaExtractionService:
    """Service for handling LlamaExtract operations"""
    
    def __init__(self):
        self.client = None
        self.agent = None
        self.jobs: Dict[str, ResumeExtractionJob] = {}
        self._agent_initialized = False
        self._use_db = settings.DATABASE_URL is not None
    
    async def initialize(self):
        """Initialize LlamaExtract client and agent"""
        if self._agent_initialized:
            return
        
        try:
            # Initialize LlamaExtract client with API key from settings
            self.client = LlamaExtract(api_key=settings.LLAMA_CLOUD_API_KEY)
            
            # Try to get existing agent or create new one
            await self._setup_agent()
            self._agent_initialized = True
            logger.info("LlamaExtract service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize LlamaExtract service: {e}")
            raise
    
    async def _setup_agent(self):
        """Setup or create LlamaExtract agent"""
        try:
            # Try to get existing agent
            self.agent = self.client.get_agent(name="resume-screening")
            logger.info(f"Using existing agent: resume-screening")
            
        except ApiError as e:
            if e.status_code == 404:
                # Agent doesn't exist, create new one
                logger.info(f"Creating new agent: {settings.LLAMA_EXTRACT_AGENT_NAME}")
                self.agent = self.client.create_agent(
                    name="resume-screening",
                    data_schema=Resume
                )
                # Save the agent configuration
                self.agent.save()
                logger.info("New agent created and saved")
            else:
                raise
    
    async def create_extraction_job(self, file_path: Path, filename: str) -> str:
        """Create a new extraction job"""
        if not self._agent_initialized:
            await self.initialize()
        
        job_id = str(uuid.uuid4())
        
        if self._use_db and async_session_maker is not None:
            # Persist to DB
            async with async_session_maker() as session:
                repo = ResumeJobRepository(session)
                await repo.create_job(job_id=job_id, filename=filename)
                await session.commit()
            logger.info(f"Created DB extraction job {job_id} for file {filename}")
            return job_id
        else:
            # In-memory fallback
            async with async_session_maker() as session:
                repo = ResumeJobRepository(session)
                await repo.create_job(job_id=job_id, filename=filename)
                await session.commit()
            logger.info(f"Created DB extraction job {job_id} for file {filename}")
            return job_id
    
    async def extract_resume_data(self, job_id: str, file_path: Path) -> ResumeExtractionJob:
        """Extract resume data from file"""
        if self._use_db and async_session_maker is not None:
            async with async_session_maker() as session:
                repo = ResumeJobRepository(session)
                await repo.set_processing(job_id)
                await session.commit()
        else:
            if job_id not in self.jobs:
                raise ValueError(f"Job {job_id} not found")
            job = self.jobs[job_id]
            job.status = "PROCESSING"
        
        try:
            logger.info(f"Starting extraction for job {job_id}")
            
            # Perform extraction using LlamaExtract
            result = self.agent.extract(str(file_path))
            
            # Validate and parse the extracted data
            if result and hasattr(result, 'data') and result.data:
                try:
                    # Convert to Resume model
                    resume_data = Resume(**result.data)
                    if self._use_db and async_session_maker is not None:
                        async with async_session_maker() as session:
                            repo = ResumeJobRepository(session)
                            await repo.set_success(
                                job_id,
                                extracted_json=resume_data.model_dump(),
                                candidate_name=resume_data.name,
                                candidate_email=resume_data.email,
                            )
                            await session.commit()
                        logger.info(f"Successfully extracted data for job {job_id} (DB)")
                    else:
                        job.extracted_data = resume_data
                        job.status = "SUCCESS"
                        job.completed_at = datetime.utcnow()
                        logger.info(f"Successfully extracted data for job {job_id}")
                    
                except ValidationError as e:
                    logger.error(f"Data validation failed for job {job_id}: {e}")
                    if self._use_db and async_session_maker is not None:
                        async with async_session_maker() as session:
                            repo = ResumeJobRepository(session)
                            await repo.set_error(job_id, f"Data validation failed: {str(e)}")
                            await session.commit()
                    else:
                        job.status = "ERROR"
                        job.error_message = f"Data validation failed: {str(e)}"
                        job.completed_at = datetime.utcnow()
            else:
                logger.error(f"No data extracted for job {job_id}")
                if self._use_db and async_session_maker is not None:
                    async with async_session_maker() as session:
                        repo = ResumeJobRepository(session)
                        await repo.set_error(job_id, "No data could be extracted from the file")
                        await session.commit()
                else:
                    job.status = "ERROR"
                    job.error_message = "No data could be extracted from the file"
                    job.completed_at = datetime.utcnow()
        
        except Exception as e:
            logger.error(f"Extraction failed for job {job_id}: {e}")
            if self._use_db and async_session_maker is not None:
                async with async_session_maker() as session:
                    repo = ResumeJobRepository(session)
                    await repo.set_error(job_id, str(e))
                    await session.commit()
            else:
                job.status = "ERROR"
                job.error_message = str(e)
                job.completed_at = datetime.utcnow()
        
        if self._use_db and async_session_maker is not None:
            async with async_session_maker() as session:
                repo = ResumeJobRepository(session)
                db_job = await repo.get_by_job_id(job_id)
                # Build API model
                extracted = None
                if db_job and db_job.extracted_json:
                    try:
                        extracted = Resume(**db_job.extracted_json)
                    except Exception:
                        extracted = None
                return ResumeExtractionJob(
                    job_id=job_id,
                    filename=db_job.filename if db_job else "",
                    status=db_job.status if db_job else "ERROR",
                    created_at=db_job.created_at if db_job else datetime.utcnow(),
                    completed_at=db_job.completed_at if db_job else None,
                    error_message=db_job.error_message if db_job else "Job not found",
                    extracted_data=extracted,
                )
        else:
            self.jobs[job_id] = job
            return job
    
    async def get_job_status(self, job_id: str) -> Optional[ResumeExtractionJob]:
        """Get job status"""
        if self._use_db and async_session_maker is not None:
            async with async_session_maker() as session:
                repo = ResumeJobRepository(session)
                db_job = await repo.get_by_job_id(job_id)
                if not db_job:
                    return None
                extracted = None
                if db_job.extracted_json:
                    try:
                        extracted = Resume(**db_job.extracted_json)
                    except Exception:
                        extracted = None
                return ResumeExtractionJob(
                    job_id=db_job.job_id,
                    filename=db_job.filename,
                    status=db_job.status,
                    created_at=db_job.created_at,
                    completed_at=db_job.completed_at,
                    error_message=db_job.error_message,
                    extracted_data=extracted,
                )
        return self.jobs.get(job_id)
    
    async def list_jobs(self, limit: int = 100, offset: int = 0) -> List[ResumeExtractionJob]:
        """List all jobs with pagination"""
        if self._use_db and async_session_maker is not None:
            async with async_session_maker() as session:
                repo = ResumeJobRepository(session)
                rows = await repo.list_jobs(limit=limit, offset=offset)
                result: List[ResumeExtractionJob] = []
                for r in rows:
                    result.append(
                        ResumeExtractionJob(
                            job_id=r.job_id,
                            filename=r.filename,
                            status=r.status,
                            created_at=r.created_at,
                            completed_at=r.completed_at,
                            error_message=r.error_message,
                            extracted_data=None,
                        )
                    )
                return result
        else:
            all_jobs = list(self.jobs.values())
            all_jobs.sort(key=lambda x: x.created_at, reverse=True)
            return all_jobs[offset:offset + limit]
    
    async def delete_job(self, job_id: str) -> bool:
        """Delete a job"""
        if self._use_db and async_session_maker is not None:
            async with async_session_maker() as session:
                repo = ResumeJobRepository(session)
                deleted = await repo.delete_job(job_id)
                await session.commit()
                if deleted:
                    logger.info(f"Deleted DB job {job_id}")
                return deleted
        if job_id in self.jobs:
            del self.jobs[job_id]
            logger.info(f"Deleted job {job_id}")
            return True
        return False
    
    def _calculate_experience_years(self, experiences: List[Any]) -> int:
        """Calculate total years of experience"""
        # Simple implementation - could be enhanced
        return len(experiences) * 2  # Assume 2 years per job on average
    
    def _normalize_skills(self, skills: List[str]) -> List[str]:
        """Normalize skills for comparison"""
        return [skill.lower().strip() for skill in skills if skill.strip()]
    
    def _calculate_skills_score(self, resume_skills: List[str], criteria: ScreeningCriteria) -> tuple:
        """Calculate skills matching score"""
        normalized_resume_skills = set(self._normalize_skills(resume_skills))
        normalized_required = set(self._normalize_skills(criteria.required_skills))
        normalized_preferred = set(self._normalize_skills(criteria.preferred_skills))
        
        matched_required = normalized_resume_skills & normalized_required
        matched_preferred = normalized_resume_skills & normalized_preferred
        missing_required = normalized_required - normalized_resume_skills
        
        # Calculate score
        required_score = len(matched_required) / max(len(normalized_required), 1)
        preferred_score = len(matched_preferred) / max(len(normalized_preferred), 1) if normalized_preferred else 0
        
        # Weighted score (required skills are more important)
        skills_score = (required_score * 0.8) + (preferred_score * 0.2)
        
        return skills_score * 100, list(matched_required), list(matched_preferred), list(missing_required)
    
    def _calculate_education_score(self, education: List[Any], criteria: ScreeningCriteria) -> float:
        """Calculate education score"""
        if not criteria.required_education_level:
            return 100.0  # If no requirement, full score
        
        education_levels = {
            'high school': 1,
            'associate': 2,
            'bachelor': 3,
            'master': 4,
            'phd': 5,
            'doctorate': 5
        }
        
        required_level = education_levels.get(criteria.required_education_level.lower(), 0)
        
        max_candidate_level = 0
        for edu in education:
            degree = getattr(edu, 'degree', '').lower()
            for level_name, level_value in education_levels.items():
                if level_name in degree:
                    max_candidate_level = max(max_candidate_level, level_value)
                    break
        
        if max_candidate_level >= required_level:
            return 100.0
        else:
            return (max_candidate_level / required_level) * 100
    
    def _calculate_experience_score(self, experiences: List[Any], criteria: ScreeningCriteria) -> float:
        """Calculate experience score"""
        if not criteria.min_years_experience:
            return 100.0
        
        total_years = self._calculate_experience_years(experiences)
        
        if total_years >= criteria.min_years_experience:
            return 100.0
        else:
            return (total_years / criteria.min_years_experience) * 100
    
    async def screen_resume(self, resume: Resume, criteria: ScreeningCriteria) -> ScreeningResult:
        """Screen a single resume against criteria"""
        
        # Combine all skills from technical_skills
        all_skills = (
            resume.technical_skills.programming_languages +
            resume.technical_skills.frameworks +
            resume.technical_skills.skills
        )
        
        # Calculate scores
        skills_score, matched_required, matched_preferred, missing_required = self._calculate_skills_score(
            all_skills, criteria
        )
        
        education_score = self._calculate_education_score(resume.education, criteria)
        experience_score = self._calculate_experience_score(resume.experience, criteria)
        
        # Calculate overall score (weighted average)
        weights = settings.DEFAULT_SCORING_WEIGHTS
        overall_score = (
            skills_score * weights["skills"] +
            experience_score * weights["experience"] +
            education_score * weights["education"]
        )
        
        # Add accomplishments bonus if present
        if resume.key_accomplishments:
            accomplishments_bonus = min(10, len(resume.key_accomplishments) / 50)  # Up to 10% bonus
            overall_score += accomplishments_bonus
        
        overall_score = min(100, overall_score)  # Cap at 100
        
        # Determine if qualified (must have all required skills and meet minimum scores)
        qualified = len(missing_required) == 0 and overall_score >= 60
        
        # Generate recommendations
        recommendations = []
        if missing_required:
            recommendations.append(f"Missing required skills: {', '.join(missing_required)}")
        if education_score < 80:
            recommendations.append("Education level below preferred requirement")
        if experience_score < 70:
            recommendations.append("Experience level below minimum requirement")
        if overall_score >= 80:
            recommendations.append("Strong candidate - recommended for interview")
        elif overall_score >= 60:
            recommendations.append("Good candidate - consider for screening call")
        else:
            recommendations.append("Below minimum requirements")
        
        return ScreeningResult(
            resume_id=str(uuid.uuid4()),  # Generate a resume ID
            candidate_name=resume.name,
            candidate_email=resume.email,
            overall_score=round(overall_score, 2),
            skills_score=round(skills_score, 2),
            experience_score=round(experience_score, 2),
            education_score=round(education_score, 2),
            matched_required_skills=matched_required,
            matched_preferred_skills=matched_preferred,
            missing_required_skills=missing_required,
            recommendations=recommendations,
            qualified=qualified
        )
    
    async def batch_screen_resumes(
        self,
        job_ids: List[str],
        criteria: ScreeningCriteria,
        include_unqualified: bool = False
    ) -> List[ScreeningResult]:
        """Screen multiple resumes against criteria"""
        results = []
        
        for job_id in job_ids:
            job = await self.get_job_status(job_id)
            if job and job.status == "SUCCESS" and job.extracted_data:
                try:
                    result = await self.screen_resume(job.extracted_data, criteria)
                    if include_unqualified or result.qualified:
                        results.append(result)
                except Exception as e:
                    logger.error(f"Failed to screen resume for job {job_id}: {e}")
        
        # Sort by overall score (descending)
        results.sort(key=lambda x: x.overall_score, reverse=True)
        
        return results
    
    async def health_check(self) -> Dict[str, Any]:
        """Check service health"""
        try:
            if not self._agent_initialized:
                await self.initialize()
            
            # Try to list agents to verify connection
            agents = self.client.list_agents()
            
            return {
                "status": "healthy",
                "agent_name": settings.LLAMA_EXTRACT_AGENT_NAME,
                "agent_available": any(agent.name == settings.LLAMA_EXTRACT_AGENT_NAME for agent in agents),
                "total_jobs": len(self.jobs),
                "pending_jobs": len([j for j in self.jobs.values() if j.status == "PENDING"]),
                "processing_jobs": len([j for j in self.jobs.values() if j.status == "PROCESSING"]),
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }


# Global service instance
extraction_service = LlamaExtractionService()


async def get_extraction_service() -> LlamaExtractionService:
    """Get extraction service instance"""
    if not extraction_service._agent_initialized:
        await extraction_service.initialize()
    return extraction_service
