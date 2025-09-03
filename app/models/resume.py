from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class Education(BaseModel):
    """Education information from resume"""
    institution: str = Field(description="The institution of the candidate")
    degree: str = Field(description="The degree of the candidate")
    start_date: Optional[str] = Field(
        default=None, description="The start date of the candidate's education"
    )
    end_date: Optional[str] = Field(
        default=None, description="The end date of the candidate's education"
    )


class Experience(BaseModel):
    """Work experience information from resume"""
    company: str = Field(description="The name of the company")
    title: str = Field(description="The title of the candidate")
    description: Optional[str] = Field(
        default=None, description="The description of the candidate's experience"
    )
    start_date: Optional[str] = Field(
        default=None, description="The start date of the candidate's experience"
    )
    end_date: Optional[str] = Field(
        default=None, description="The end date of the candidate's experience"
    )


class TechnicalSkills(BaseModel):
    programming_languages: List[str] = Field(
        description="The programming languages the candidate is proficient in."
    )
    frameworks: List[str] = Field(
        description="The tools/frameworks the candidate is proficient in, e.g. React, Django, PyTorch, etc."
    )
    skills: List[str] = Field(
        description="Other general skills the candidate is proficient in, e.g. Data Engineering, Machine Learning, etc."
    )


class Resume(BaseModel):
    name: str = Field(description="The name of the candidate")
    email: str = Field(description="The email address of the candidate")
    links: List[str] = Field(
        description="The links to the candidate's social media profiles"
    )
    experience: List[Experience] = Field(description="The candidate's experience")
    education: List[Education] = Field(description="The candidate's education")
    technical_skills: TechnicalSkills = Field(
        description="The candidate's technical skills"
    )
    key_accomplishments: str = Field(
        description="Summarize the candidates highest achievements."
    )


class ResumeExtractionJob(BaseModel):
    """Resume extraction job status and metadata"""
    job_id: str = Field(description="Unique job identifier")
    filename: str = Field(description="Original filename of uploaded resume")
    status: str = Field(description="Job status: PENDING, PROCESSING, SUCCESS, ERROR")
    created_at: datetime = Field(description="Job creation timestamp")
    completed_at: Optional[datetime] = Field(default=None, description="Job completion timestamp")
    error_message: Optional[str] = Field(default=None, description="Error message if job failed")
    extracted_data: Optional[Resume] = Field(default=None, description="Extracted resume data")


class ScreeningCriteria(BaseModel):
    """Criteria for screening resumes"""
    required_skills: List[str] = Field(
        default_factory=list,
        description="Skills that are required for the position"
    )
    preferred_skills: List[str] = Field(
        default_factory=list,
        description="Skills that are preferred but not required"
    )
    min_years_experience: Optional[int] = Field(
        default=None,
        description="Minimum years of experience required"
    )
    required_education_level: Optional[str] = Field(
        default=None,
        description="Required education level (e.g., 'Bachelor', 'Master', 'PhD')"
    )
    keywords: List[str] = Field(
        default_factory=list,
        description="Keywords to search for in experience descriptions"
    )


class ScreeningResult(BaseModel):
    """Result of resume screening against criteria"""
    resume_id: str = Field(description="Resume identifier")
    candidate_name: str = Field(description="Candidate name")
    candidate_email: str = Field(description="Candidate email")
    overall_score: float = Field(description="Overall screening score (0-100)")
    skills_score: float = Field(description="Skills matching score (0-100)")
    experience_score: float = Field(description="Experience score (0-100)")
    education_score: float = Field(description="Education score (0-100)")
    matched_required_skills: List[str] = Field(description="Required skills found in resume")
    matched_preferred_skills: List[str] = Field(description="Preferred skills found in resume")
    missing_required_skills: List[str] = Field(description="Required skills missing from resume")
    recommendations: List[str] = Field(description="Screening recommendations")
    qualified: bool = Field(description="Whether candidate meets minimum requirements")
