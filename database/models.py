"""Data models for candidate profile, job descriptions, evaluations, and applications."""
from datetime import datetime, timezone
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class EducationEntry(BaseModel):
    institution: str = ""
    degree: str = ""
    year: str = ""


class ExperienceEntry(BaseModel):
    company: str = ""
    title: str = ""
    dates: str = ""
    description: str = ""


class ProjectEntry(BaseModel):
    name: str = ""
    tech_stack: str = ""
    description: str = ""


class CandidateProfile(BaseModel):
    """Pydantic model representing candidate profile dynamically extracted from resume."""

    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    education: List[EducationEntry] = Field(default_factory=list)
    experience: List[ExperienceEntry] = Field(default_factory=list)
    projects: List[ProjectEntry] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list)
    programming_languages: List[str] = Field(default_factory=list)
    frameworks: List[str] = Field(default_factory=list)
    libraries: List[str] = Field(default_factory=list)
    databases: List[str] = Field(default_factory=list)
    cloud_technologies: List[str] = Field(default_factory=list)
    developer_tools: List[str] = Field(default_factory=list)
    ai_ml_skills: List[str] = Field(default_factory=list)
    automation_skills: List[str] = Field(default_factory=list)
    inferred_careers: List[str] = Field(default_factory=list)
    inferred_domains: List[str] = Field(default_factory=list)
    inferred_job_titles: List[str] = Field(default_factory=list)
    inferred_search_queries: List[str] = Field(default_factory=list)
    raw_text_hash: str


class JobListing(BaseModel):
    """Model representing a job posting discovered from a job board or site."""

    id: Optional[int] = None
    title: str
    company: str
    location: str
    source_url: str
    source_platform: str
    raw_description: str
    salary_range: Optional[str] = None
    employment_type: Optional[str] = None
    posted_date: Optional[str] = None
    fingerprint: str  # Hash of company + title + source_url
    created_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))


class JobEvaluation(BaseModel):
    """Model representing an LLM match evaluation for a specific job."""

    id: Optional[int] = None
    job_id: int
    overall_match_score: float  # 0 to 100
    skills_score: float
    tech_stack_score: float
    experience_score: float
    domain_score: float
    ats_keyword_score: float
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    reasoning: str
    decision: str  # APPLY, MAYBE, REJECT
    evaluated_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))


class JobApplication(BaseModel):
    """Model tracking application lifecycle and status."""

    id: Optional[int] = None
    job_id: int
    status: str  # QUEUED, APPLIED, HITL_PAUSED, INTERVIEW, ASSESSMENT, REJECTED, OFFER
    applied_at: Optional[datetime] = None
    resume_file_used: str
    cover_letter_text: Optional[str] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))
