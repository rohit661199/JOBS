"""Application Decision Engine implementing strict guardrails, experience checks, and threshold evaluation."""
import re
from typing import Tuple
from config.settings import settings
from database.models import CandidateProfile, JobListing
from utils.logger import logger


class DecisionEngine:
    """Evaluates whether a candidate should apply, maybe apply, or reject a job opportunity."""

    HIGH_EXP_PATTERNS = [
        r"\b[2-9]\s*\+\s*years?\b",
        r"\b1[0-9]\s*\+\s*years?\b",
        r"\b[3-9]\s*to\s*[1-9][0-9]?\s*years?\b",
        r"\bsenior\b",
        r"\blead\b",
        r"\bprincipal\b",
        r"\barchitect\b",
        r"\bstaff\b",
        r"\bmanager\b",
        r"\bvp\b",
        r"\bdirector\b",
    ]

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
        # 1. Company Blacklist Check
        for company in self.settings.blacklist_companies:
            if company.lower() in job.company.lower():
                msg = f"REJECTED: Company '{job.company}' is in candidate blacklist."
                logger.info(msg)
                return "REJECT", msg

        # 2. Title & Description Blacklist Check
        for kw in self.settings.blacklist_keywords:
            if kw.lower() in job.title.lower():
                msg = f"REJECTED: Job title contains blacklisted term '{kw}'."
                logger.info(msg)
                return "REJECT", msg

        # 3. Fresher (0 Experience) Enforcement Check
        if self.settings.max_experience_gap_years <= 1 or "fresher" in self.settings.seniority_level.lower():
            text_to_check = (job.title + " " + job.raw_description).lower()
            for pattern in self.HIGH_EXP_PATTERNS:
                if re.search(pattern, text_to_check):
                    msg = f"REJECTED: Candidate is a Fresher (0 years exp). Job requires high experience ('{pattern}')."
                    logger.info(msg)
                    return "REJECT", msg

        # 4. Match Score Threshold Gate
        min_threshold = self.settings.match_threshold
        if overall_score < (min_threshold - 15):
            msg = f"REJECTED: Overall match score ({overall_score}) is far below threshold ({min_threshold})."
            logger.info(msg)
            return "REJECT", msg
        elif overall_score < min_threshold:
            msg = f"MAYBE: Match score ({overall_score}) is slightly below threshold ({min_threshold}). Requires review."
            logger.info(msg)
            return "MAYBE", msg

        # 5. Passed all filters -> APPLY
        logger.info(f"ACCEPTED: High-match fresher opportunity ({overall_score} >= {min_threshold}). Status: APPLY.")
        return "APPLY", reasoning
