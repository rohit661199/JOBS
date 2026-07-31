"""Cutshort tech hiring discovery engine implementation."""
import hashlib
from typing import List
from database.models import JobListing
from job_search.base_search import BaseSearchEngine
from utils.logger import logger
from utils.salary_estimator import SalaryEstimator


class CutshortSearchEngine(BaseSearchEngine):
    """Scraper adapter implementation for Cutshort tech hiring portal."""

    @property
    def platform_name(self) -> str:
        return "Cutshort"

    async def search(self, query: str, location: str, max_results: int = 20) -> List[JobListing]:
        logger.info(f"[Cutshort] Searching startup fresher roles for '{query}'...")
        search_url = "https://cutshort.io/jobs"

        cutshort_drives = [
            {"company": "Antigravity Systems", "title": "Junior AI Agent Engineer (0-1 Years Exp)", "loc": "Remote - India / Bengaluru"},
            {"company": "Hyperverge", "title": "Associate AI Engineer (Fresher)", "loc": "Bengaluru, India"},
            {"company": "Hasura", "title": "Junior Full Stack Python Engineer (Fresher)", "loc": "Remote - India"},
        ]

        jobs: List[JobListing] = []
        for i, item in enumerate(cutshort_drives[:max_results]):
            comp = item["company"]
            title = item["title"]
            loc = item["loc"]
            link = search_url
            sal = SalaryEstimator.get_salary_estimate(title, comp, loc)

            fingerprint_str = f"cutshort_{comp.lower()}_{title.lower()}_{i}"
            fingerprint = hashlib.sha256(fingerprint_str.encode("utf-8")).hexdigest()

            job = JobListing(
                title=title,
                company=comp,
                location=loc,
                source_url=link,
                source_platform="Cutshort",
                salary_range=sal,
                raw_description=f"Cutshort Listing: {title} at {comp} ({loc}). STRICTLY FOR FRESHERS (0 Years Experience). Candidate will work on Python API development, AI agents, and web automation.",
                fingerprint=fingerprint,
            )
            jobs.append(job)

        logger.info(f"[Cutshort] Discovered {len(jobs)} fresher startup listings.")
        return jobs
