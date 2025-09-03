from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import ResumeJob, ScreeningResult


class ResumeJobRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_job(self, job_id: str, filename: str) -> ResumeJob:
        job = ResumeJob(
            job_id=job_id,
            filename=filename,
            status="PENDING",
            created_at=datetime.utcnow(),
        )
        print(f"Creating job----: {job}")
        self.session.add(job)
        await self.session.flush()
        return job

    async def set_processing(self, job_id: str) -> None:
        await self.session.execute(
            update(ResumeJob).where(ResumeJob.job_id == job_id).values(status="PROCESSING")
        )

    async def set_success(self, job_id: str, extracted_json: dict, candidate_name: Optional[str], candidate_email: Optional[str]) -> None:
        await self.session.execute(
            update(ResumeJob)
            .where(ResumeJob.job_id == job_id)
            .values(
                status="SUCCESS",
                completed_at=datetime.utcnow(),
                error_message=None,
                extracted_json=extracted_json,
                candidate_name=candidate_name,
                candidate_email=candidate_email,
            )
        )

    async def set_error(self, job_id: str, error_message: str) -> None:
        await self.session.execute(
            update(ResumeJob)
            .where(ResumeJob.job_id == job_id)
            .values(status="ERROR", completed_at=datetime.utcnow(), error_message=error_message)
        )

    async def get_by_job_id(self, job_id: str) -> Optional[ResumeJob]:
        result = await self.session.execute(select(ResumeJob).where(ResumeJob.job_id == job_id))
        return result.scalar_one_or_none()

    async def list_jobs(self, limit: int, offset: int) -> List[ResumeJob]:
        result = await self.session.execute(
            select(ResumeJob).order_by(ResumeJob.created_at.desc()).limit(limit).offset(offset)
        )
        return list(result.scalars().all())

    async def delete_job(self, job_id: str) -> bool:
        result = await self.session.execute(delete(ResumeJob).where(ResumeJob.job_id == job_id))
        return result.rowcount > 0


class ScreeningResultRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_for_job(
        self,
        job_pk: int,
        overall_score: float,
        skills_score: float,
        experience_score: float,
        education_score: float,
        qualified: bool,
        matched_required_skills: Optional[list[str]],
        matched_preferred_skills: Optional[list[str]],
        missing_required_skills: Optional[list[str]],
        recommendations: Optional[list[str]],
    ) -> ScreeningResult:
        result = ScreeningResult(
            job_id_fk=job_pk,
            overall_score=overall_score,
            skills_score=skills_score,
            experience_score=experience_score,
            education_score=education_score,
            qualified=qualified,
            matched_required_skills=matched_required_skills,
            matched_preferred_skills=matched_preferred_skills,
            missing_required_skills=missing_required_skills,
            recommendations=recommendations,
        )
        self.session.add(result)
        await self.session.flush()
        return result


