"""Abstract base search engine interface for job platform scrapers."""
from abc import ABC, abstractmethod
from typing import List
from database.models import CandidateProfile, JobListing


class BaseSearchEngine(ABC):
    """Abstract interface for all site-specific job search engines."""

    @property
    @abstractmethod
    def platform_name(self) -> str:
        """Returns the human-readable platform name (e.g. 'LinkedIn')."""
        pass

    @abstractmethod
    async def search(self, query: str, location: str, max_results: int = 20) -> List[JobListing]:
        """Performs search on platform and returns normalized JobListing objects.

        Args:
            query: Search query terms.
            location: Target geographic location or 'Remote'.
            max_results: Maximum job listings to retrieve.

        Returns:
            List of discovered JobListing objects.
        """
        pass
