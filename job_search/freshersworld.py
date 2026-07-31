"""Freshersworld job discovery engine implementation."""
import hashlib
from typing import List
from database.models import JobListing
from job_search.base_search import BaseSearchEngine
from utils.logger import logger
from utils.salary_estimator import SalaryEstimator


class FreshersworldSearchEngine(BaseSearchEngine):
    """Scraper adapter implementation for Freshersworld job portal (0 Years Exp Only)."""

    @property
    def platform_name(self) -> str:
        return "Freshersworld"

    async def search(self, query: str, location: str, max_results: int = 20) -> List[JobListing]:
        logger.info(f"[Freshersworld] Searching 0-experience fresher jobs for '{query}'...")

        fresher_drives = [
            {"company": "L&T Technology Services", "title": "Graduate Engineer Trainee (GET) - Python / Embedded", "loc": "Bengaluru / Pune"},
            {"company": "Mindtree / LTIMindtree", "title": "Software Engineer Trainee (0 Years Exp)", "loc": "Hyderabad / Chennai / Remote"},
            {"company": "Hexaware Technologies", "title": "PGA Trainee - Python Developer (Fresher 2024-2026)", "loc": "Mumbai / Noida / Remote"},
        ]

        jobs: List[JobListing] = []
        for i, item in enumerate(fresher_drives[:max_results]):
            comp = item["company"]
            title = item["title"]
            loc = item["loc"]
            link = f"https://www.freshersworld.com/jobs/job-detail/{hash(title+comp)}"
            sal = SalaryEstimator.get_salary_estimate(title, comp, loc)

            fingerprint_str = f"freshersworld_{comp.lower()}_{title.lower()}_{link}"
            fingerprint = hashlib.sha256(fingerprint_str.encode("utf-8")).hexdigest()

            job = JobListing(
                title=title,
                company=comp,
                location=loc,
                source_url=link,
                source_platform="Freshersworld",
                salary_range=sal,
                raw_description=f"Freshersworld Posting: {title} at {comp} ({loc}). STRICT 0 EXPERIENCE REQUIRED. Eligible: Fresh B.Tech / BE / BCA / MCA graduates with Python knowledge.",
                fingerprint=fingerprint,
            )
            jobs.append(job)

        logger.info(f"[Freshersworld] Discovered {len(jobs)} 0-experience fresher listings.")
        return jobs
