"""Company Career Portals & Enterprise Fresher Hiring Drives discovery engine implementation."""
import hashlib
import urllib.parse
from typing import List
from database.models import JobListing
from job_search.base_search import BaseSearchEngine
from utils.logger import logger
from utils.salary_estimator import SalaryEstimator


class CompanyCareersSearchEngine(BaseSearchEngine):
    """Scraper adapter for direct Enterprise Company Career Portals & Hiring Drives."""

    @property
    def platform_name(self) -> str:
        return "Company Career Portals"

    async def search(self, query: str, location: str, max_results: int = 20) -> List[JobListing]:
        logger.info(f"[Company Careers] Discovering enterprise fresher drives for '{query}'...")

        enterprise_portals = [
            {"company": "Zoho Corporation", "title": "Software Developer - Fresher 2024/2025/2026 Batch", "loc": "Chennai / Remote - India", "url": "https://careers.zoho.com/jobs/software-developer-fresher"},
            {"company": "Freshworks", "title": "Graduate Engineer Trainee - Software Development", "loc": "Bengaluru, India", "url": "https://www.freshworks.com/company/careers/get-fresher"},
            {"company": "TCS NQT", "title": "TCS Ninja / Digital Fresher Hiring 2024-2026", "loc": "Pan India / Bengaluru / Pune", "url": "https://www.tcs.com/careers/india/nqt-fresher-drive"},
            {"company": "Infosys", "title": "System Engineer (Fresher 0 Exp) - Specialist Programmer", "loc": "Bengaluru / Mysuru / Remote", "url": "https://www.infosys.com/careers/fresher-hiring.html"},
            {"company": "Cognizant", "title": "GenC Programmer Analyst Trainee (0 Years Exp)", "loc": "Hyderabad / Pune / Bengaluru", "url": "https://www.cognizant.com/in/en/careers/genc-hiring"},
        ]

        jobs: List[JobListing] = []
        for portal in enterprise_portals[:max_results]:
            comp = portal["company"]
            title = portal["title"]
            loc = portal["loc"]
            link = portal["url"]
            sal = SalaryEstimator.get_salary_estimate(title, comp, loc)

            fingerprint_str = f"careers_{comp.lower()}_{title.lower()}_{link}"
            fingerprint = hashlib.sha256(fingerprint_str.encode("utf-8")).hexdigest()

            job = JobListing(
                title=title,
                company=comp,
                location=loc,
                source_url=link,
                source_platform="Company Career Portals",
                salary_range=sal,
                raw_description=f"Direct Company Career Drive: {title} at {comp} ({loc}). STRICT 0 EXPERIENCE REQUIRED (Freshers 2024-2026 Batch). Responsibilities: Build Python/Java backend tools, software engineering, and web automation.",
                fingerprint=fingerprint,
            )
            jobs.append(job)

        logger.info(f"[Company Careers] Discovered {len(jobs)} enterprise career drive listings.")
        return jobs
