"""Job Description Evaluator using LLM analysis and weighted scoring."""
from typing import Optional
from database.models import CandidateProfile, JobEvaluation, JobListing
from database.repository import JobRepository
from llm.base import BaseLLMProvider
from llm.factory import get_llm_provider
from llm.prompts import JOB_MATCHING_SYSTEM_PROMPT
from matcher.decision_engine import DecisionEngine
from matcher.scoring import MatchScorer
from utils.logger import logger


class JobEvaluator:
    """Evaluates job descriptions against candidate profiles using LLMs and weighted matrix."""

    def __init__(self, llm_provider: Optional[BaseLLMProvider] = None, repo: Optional[JobRepository] = None):
        self.llm = llm_provider or get_llm_provider()
        self.repo = repo or JobRepository()
        self.decision_engine = DecisionEngine()

    def evaluate_job(self, job: JobListing, candidate_profile: CandidateProfile) -> JobEvaluation:
        """Runs LLM evaluation on a job description with heuristic fallback.

        Args:
            job: Discovered JobListing model instance.
            candidate_profile: CandidateProfile model instance.

        Returns:
            Populated JobEvaluation model instance.
        """
        logger.info(f"Evaluating job #{job.id}: '{job.title}' at {job.company}")

        prompt = f"""
Candidate Technical Capabilities & Experience:
{candidate_profile.model_dump_json(indent=2)}

Target Job Posting:
Title: {job.title}
Company: {job.company}
Location: {job.location}
Description:
{job.raw_description}

Perform a rigorous evaluation. Return scores (0-100) for skills_score, tech_stack_score, experience_score, domain_score, ats_keyword_score, and strengths/weaknesses list.
"""

        try:
            class LLMRating(JobEvaluation):
                job_id: int = 0
                overall_match_score: float = 0.0

            rating = self.llm.structured_output(
                prompt=prompt,
                schema=LLMRating,
                system_prompt=JOB_MATCHING_SYSTEM_PROMPT
            )
            skills_score = rating.skills_score
            tech_stack_score = rating.tech_stack_score
            experience_score = rating.experience_score
            domain_score = rating.domain_score
            ats_keyword_score = rating.ats_keyword_score
            strengths = rating.strengths
            weaknesses = rating.weaknesses
            reasoning = rating.reasoning

        except Exception as e:
            logger.warning(f"LLM API error ({e}) on job evaluation. Using heuristic matching matrix fallback.")
            skills_score, tech_stack_score, experience_score, domain_score, ats_keyword_score, strengths, weaknesses, reasoning = self._heuristic_match_evaluation(job, candidate_profile)

        overall_score = MatchScorer.calculate_overall_score(
            skills_score=skills_score,
            tech_stack_score=tech_stack_score,
            experience_score=experience_score,
            domain_score=domain_score,
            ats_keyword_score=ats_keyword_score,
        )

        decision, updated_reasoning = self.decision_engine.evaluate_decision(
            overall_score=overall_score,
            job=job,
            candidate_profile=candidate_profile,
            reasoning=reasoning
        )

        evaluation = JobEvaluation(
            job_id=job.id,
            overall_match_score=overall_score,
            skills_score=skills_score,
            tech_stack_score=tech_stack_score,
            experience_score=experience_score,
            domain_score=domain_score,
            ats_keyword_score=ats_keyword_score,
            strengths=strengths,
            weaknesses=weaknesses,
            reasoning=updated_reasoning,
            decision=decision,
        )

        self.repo.save_evaluation(evaluation)
        return evaluation

    def _heuristic_match_evaluation(self, job: JobListing, profile: CandidateProfile):
        """Rule-based heuristic matching matrix when LLM API keys are unconfigured."""
        cand_skills = set(profile.programming_languages + profile.frameworks + profile.cloud_technologies)
        jd_text = (job.title + " " + job.raw_description).lower()

        overlap = sum(1 for s in cand_skills if s.lower() in jd_text)
        score = min(100.0, max(50.0, overlap * 25.0))

        strengths = [f"Matches technical skills: {', '.join(list(cand_skills)[:3])}"]
        weaknesses = ["Detailed ATS review requires valid GEMINI_API_KEY"]
        reasoning = f"Heuristic evaluation score {score}% based on direct keyword overlap."

        return score, score, score, score, score, strengths, weaknesses, reasoning
