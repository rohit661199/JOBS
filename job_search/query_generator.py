"""Dynamic Search Query Generator converting candidate profiles into search keywords."""
from typing import List
from database.models import CandidateProfile
from utils.logger import logger


class SearchQueryGenerator:
    """Generates targeted job board search terms dynamically from CandidateProfile."""

    @staticmethod
    def generate_queries(profile: CandidateProfile, locations: List[str]) -> List[str]:
        """Combines inferred job titles and skills into search queries.

        Args:
            profile: CandidateProfile extracted from resume.
            locations: User preferred locations list.

        Returns:
            List of generated search query strings.
        """
        queries = set()

        # 1. Add inferred search queries directly from candidate profile
        for q in profile.inferred_search_queries:
            if q.strip():
                queries.add(q.strip())

        # 2. Combine top inferred job titles with key programming languages
        top_titles = profile.inferred_job_titles[:3] if profile.inferred_job_titles else ["Software Engineer"]
        top_langs = profile.programming_languages[:2] if profile.programming_languages else []

        for title in top_titles:
            queries.add(title)
            for lang in top_langs:
                queries.add(f"{lang} {title}")

        result_queries = list(queries)
        logger.info(f"Generated {len(result_queries)} dynamic search queries: {result_queries[:5]}")
        return result_queries
