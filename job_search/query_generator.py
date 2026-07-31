"""Dynamic Search Query Generator converting candidate profiles into fresher & entry-level search keywords."""
from typing import List
from database.models import CandidateProfile
from utils.logger import logger


class SearchQueryGenerator:
    """Generates targeted job board search terms dynamically for Freshers (0 years experience)."""

    @staticmethod
    def generate_queries(profile: CandidateProfile, locations: List[str]) -> List[str]:
        """Combines inferred fresher job titles and skills into entry-level search queries.

        Args:
            profile: CandidateProfile extracted from resume.
            locations: User preferred locations list.

        Returns:
            List of generated search query strings targeting 0 years experience / Freshers.
        """
        queries = set()

        # 1. Dynamic Fresher search queries
        top_langs = profile.programming_languages[:2] if profile.programming_languages else ["Python"]

        for lang in top_langs:
            queries.add(f"{lang} Developer Fresher")
            queries.add(f"Graduate Engineer Trainee {lang}")
            queries.add(f"Junior {lang} Developer 0 Years")
            queries.add(f"Associate {lang} Software Engineer")

        queries.add("Software Engineer Fresher")
        queries.add("Graduate Engineer Trainee")
        queries.add("Junior AI Developer 0 Years")

        result_queries = list(queries)
        logger.info(f"Generated {len(result_queries)} dynamic fresher search queries: {result_queries[:5]}")
        return result_queries
