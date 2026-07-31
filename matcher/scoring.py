"""Weighted multi-criterion match scoring algorithm."""
from typing import Dict
from config.settings import settings


class MatchScorer:
    """Calculates weighted overall match score (0-100) based on sub-criterion ratings."""

    @staticmethod
    def calculate_overall_score(
        skills_score: float,
        tech_stack_score: float,
        experience_score: float,
        domain_score: float,
        ats_keyword_score: float,
        custom_weights: Dict[str, float] = None
    ) -> float:
        """Computes weighted overall match score.

        Default weights:
        - Skills: 25%
        - Tech Stack: 25%
        - Experience: 20%
        - Domain Alignment: 15%
        - ATS Keyword Similarity: 15%
        """
        weights = custom_weights or {
            "skills": 0.25,
            "tech_stack": 0.25,
            "experience": 0.20,
            "domain": 0.15,
            "ats_keywords": 0.15,
        }

        total_weight = sum(weights.values())
        if total_weight <= 0:
            total_weight = 1.0

        raw_weighted_score = (
            (skills_score * weights.get("skills", 0.25)) +
            (tech_stack_score * weights.get("tech_stack", 0.25)) +
            (experience_score * weights.get("experience", 0.20)) +
            (domain_score * weights.get("domain", 0.15)) +
            (ats_keyword_score * weights.get("ats_keywords", 0.15))
        )

        final_score = round(raw_weighted_score / total_weight, 2)
        return max(0.0, min(100.0, final_score))
