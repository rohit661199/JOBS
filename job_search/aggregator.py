"""Multi-source job aggregator executing asynchronous searches across 11+ platforms and career drives."""
import asyncio
from typing import List, Optional
from config.settings import settings
from database.models import CandidateProfile, JobListing
from database.repository import JobRepository
from job_search.base_search import BaseSearchEngine
from job_search.company_careers import CompanyCareersSearchEngine
from job_search.cutshort import CutshortSearchEngine
from job_search.freshersworld import FreshersworldSearchEngine
from job_search.glassdoor import GlassdoorSearchEngine
from job_search.indeed import IndeedSearchEngine
from job_search.internshala import InternshalaSearchEngine
from job_search.linkedin import LinkedInSearchEngine
from job_search.naukri import NaukriSearchEngine
from job_search.query_generator import SearchQueryGenerator
from job_search.remote_ok import RemoteOKSearchEngine
from job_search.unstop import UnstopSearchEngine
from job_search.wellfound import WellfoundSearchEngine
from utils.logger import logger


class JobSearchAggregator:
    """Orchestrates job discovery queries across 11+ search platforms and enterprise career drives."""

    def __init__(self, engines: Optional[List[BaseSearchEngine]] = None, repo: Optional[JobRepository] = None):
        self.engines = engines or [
            LinkedInSearchEngine(),
            IndeedSearchEngine(),
            GlassdoorSearchEngine(),
            NaukriSearchEngine(),
            WellfoundSearchEngine(),
            RemoteOKSearchEngine(),
            InternshalaSearchEngine(),
            CompanyCareersSearchEngine(),
            UnstopSearchEngine(),
            FreshersworldSearchEngine(),
            CutshortSearchEngine()
        ]
        self.repo = repo or JobRepository()

    async def execute_discovery_cycle(self, profile: CandidateProfile) -> List[JobListing]:
        """Runs multi-source discovery queries derived from candidate profile.

        Args:
            profile: Extracted CandidateProfile.

        Returns:
            List of newly discovered, deduplicated JobListing objects saved to DB.
        """
        queries = SearchQueryGenerator.generate_queries(profile, settings.locations)
        locations = settings.locations or ["India"]

        discovered_jobs: List[JobListing] = []
        newly_saved_jobs: List[JobListing] = []

        logger.info(f"Initiating multi-source discovery cycle across {len(self.engines)} search platforms & career drives...")

        for query in queries[:3]:
            for location in locations[:2]:
                for engine in self.engines:
                    try:
                        results = await engine.search(query=query, location=location, max_results=10)
                        discovered_jobs.extend(results)
                    except Exception as e:
                        logger.error(f"Search engine error on {engine.platform_name}: {e}")

        # Deduplicate and save to repository
        for job in discovered_jobs:
            job_id = self.repo.add_job(job)
            if job_id:
                job.id = job_id
                newly_saved_jobs.append(job)

        logger.info(f"Discovery cycle completed. Total new jobs added to database: {len(newly_saved_jobs)}")
        return newly_saved_jobs
