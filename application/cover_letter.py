"""Cover letter generator adhering strictly to zero-hallucination factual bounds."""
from typing import Optional
from database.models import CandidateProfile, JobListing
from llm.base import BaseLLMProvider
from llm.factory import get_llm_provider
from llm.prompts import COVER_LETTER_SYSTEM_PROMPT
from utils.logger import logger


class CoverLetterGenerator:
    """Generates tailored, concise cover letters using candidate resume facts."""

    def __init__(self, llm_provider: Optional[BaseLLMProvider] = None):
        self.llm = llm_provider or get_llm_provider()

    def generate(self, profile: CandidateProfile, job: JobListing) -> str:
        """Generates factual cover letter string.

        Args:
            profile: CandidateProfile instance.
            job: Target JobListing instance.

        Returns:
            Plain text cover letter.
        """
        logger.info(f"Generating tailored cover letter for '{job.title}' at {job.company}...")

        prompt = f"""
Candidate Profile:
Name: {profile.full_name or 'Candidate'}
Programming Languages: {', '.join(profile.programming_languages)}
Frameworks: {', '.join(profile.frameworks)}
Cloud/AI Tech: {', '.join(profile.cloud_technologies + profile.ai_ml_skills)}

Job Information:
Title: {job.title}
Company: {job.company}
Description: {job.raw_description[:1000]}

Write a concise 3-paragraph professional cover letter addressing the hiring manager.
"""

        try:
            letter = self.llm.generate(prompt=prompt, system_prompt=COVER_LETTER_SYSTEM_PROMPT)
            return letter
        except Exception as e:
            logger.error(f"Failed to generate cover letter: {e}")
            return f"Dear Hiring Team at {job.company},\n\nI am writing to express my strong interest in the {job.title} position. Given my background, I look forward to connecting."
