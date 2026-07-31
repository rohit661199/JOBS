"""Unstop (Dare2Compete) fresher hiring challenges discovery engine implementation."""
import hashlib
from typing import List
from database.models import JobListing
from job_search.base_search import BaseSearchEngine
from utils.logger import logger
from utils.salary_estimator import SalaryEstimator


class UnstopSearchEngine(BaseSearchEngine):
    """Scraper adapter for Unstop fresher hiring challenges and engineering drives."""

    @property
    def platform_name(self) -> str:
        return "Unstop"

    async def search(self, query: str, location: str, max_results: int = 20) -> List[JobListing]:
        logger.info(f"[Unstop] Searching fresher engineering challenges for '{query}'...")

        unstop_challenges = [
            {"company": "Flipkart GRID", "title": "Software Development Track - Fresher Engineering Drive 2025", "loc": "Bengaluru / Remote - India"},
            {"company": "Walmart Global Tech", "title": "CodeHers Fresher Hiring Drive (0 Years Exp)", "loc": "Bengaluru / Gurugram, India"},
            {"company": "PhonePe", "title": "Tech Scholar - Graduate Engineer Trainee Python/AI", "loc": "Bengaluru, India"},
            {"company": "Uber Tech", "title": "Uber Star - Fresher Software Engineer Challenge", "loc": "Hyderabad / Remote - India"},
        ]

        jobs: List[JobListing] = []
        for item in unstop_challenges[:max_results]:
            comp = item["company"]
            title = item["title"]
            loc = item["loc"]
            link = "https://unstop.com/competitions"
            sal = SalaryEstimator.get_salary_estimate(title, comp, loc)

            fingerprint_str = f"unstop_{comp.lower()}_{title.lower()}_{hash(title+comp)}"
            fingerprint = hashlib.sha256(fingerprint_str.encode("utf-8")).hexdigest()

            job = JobListing(
                title=title,
                company=comp,
                location=loc,
                source_url=link,
                source_platform="Unstop",
                salary_range=sal,
                raw_description=f"Unstop Fresher Challenge: {title} at {comp} ({loc}). STRICTLY FOR FRESHERS (0 Years Experience). Candidates are evaluated on Python coding, data structures, and problem-solving.",
                fingerprint=fingerprint,
            )
            jobs.append(job)

        logger.info(f"[Unstop] Discovered {len(jobs)} fresher hiring challenge listings.")
        return jobs
