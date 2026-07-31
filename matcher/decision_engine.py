"""Application Decision Engine implementing strict guardrails and threshold evaluation."""
from typing import Tuple
from config.settings import settings
from database.models import CandidateProfile, JobListing
from utils.logger import logger


class DecisionEngine:
    """Evaluates whether a candidate should apply, maybe apply, or reject a job opportunity."""

    def __init__(self):
        self.settings = settings

    def evaluate_decision(
        self,
        overall_score: float,
        job: JobListing,
        candidate_profile: CandidateProfile,
        reasoning: str
    ) -> Tuple[str, str]:
        """Determines application action: APPLY, MAYBE, or REJECT.

        Returns:
            Tuple of (Decision_String, Final_Reasoning)
        """
        # 1. Blacklist Check
        for company in self.settings.blacklist_companies:
            if company.lower() in job.company.lower():
                msg = f"REJECTED: Company '{job.company}' is in candidate blacklist."
                logger.info(msg)
                return "REJECT", msg

        for kw in self.settings.blacklist_keywords:
            if kw.lower() in job.title.lower() or kw.lower() in job.raw_description.lower():
                msg = f"REJECTED: Job title or description contains blacklisted term '{kw}'."
                logger.info(msg)
                return "REJECT", msg

        # 2. Match Score Threshold Gate
        min_threshold = self.settings.match_threshold
        if overall_score < (min_threshold - 15):
            msg = f"REJECTED: Overall match score ({overall_score}) is far below threshold ({min_threshold})."
            logger.info(msg)
            return "REJECT", msg
        elif overall_score < min_threshold:
            msg = f"MAYBE: Match score ({overall_score}) is slightly below threshold ({min_threshold}). Requires review."
            logger.info(msg)
            return "MAYBE", msg

        # 3. Passed all filters -> APPLY
        logger.info(f"ACCEPTED: High-match opportunity ({overall_score} >= {min_threshold}). Status: APPLY.")
        return "APPLY", reasoning
