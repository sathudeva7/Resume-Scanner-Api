from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class ResumeJob(Base):
    __tablename__ = "resume_jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    job_id: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    filename: Mapped[str] = mapped_column(String(512), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=False), nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Denormalize some candidate info for quick listing (optional)
    candidate_name: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    candidate_email: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)

    # Raw extracted JSON (Pydantic dict)
    extracted_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    screenings: Mapped[list[ScreeningResult]] = relationship(
        back_populates="job", cascade="all, delete-orphan"
    )


class ScreeningResult(Base):
    __tablename__ = "screening_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    job_id_fk: Mapped[int] = mapped_column(ForeignKey("resume_jobs.id", ondelete="CASCADE"), index=True)

    # Summary
    overall_score: Mapped[float] = mapped_column()
    skills_score: Mapped[float] = mapped_column()
    experience_score: Mapped[float] = mapped_column()
    education_score: Mapped[float] = mapped_column()
    qualified: Mapped[bool] = mapped_column()

    # Matched/missing skills and recommendations as JSON arrays
    matched_required_skills: Mapped[Optional[list[str]]] = mapped_column(JSON, nullable=True)
    matched_preferred_skills: Mapped[Optional[list[str]]] = mapped_column(JSON, nullable=True)
    missing_required_skills: Mapped[Optional[list[str]]] = mapped_column(JSON, nullable=True)
    recommendations: Mapped[Optional[list[str]]] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False, default=datetime.utcnow)

    job: Mapped[ResumeJob] = relationship(back_populates="screenings")


