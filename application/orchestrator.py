"""End-to-end execution orchestrator coordinating search, match evaluation, and browser application pipeline."""
import asyncio
from typing import Dict, List, Optional
from config.settings import settings
from database.models import CandidateProfile, JobApplication, JobListing
from database.repository import JobRepository
from job_search.aggregator import JobSearchAggregator
from matcher.evaluator import JobEvaluator
from notifications.notifier import NotificationManager
from resume.analyzer import ResumeAnalyzer
from utils.logger import logger


class ApplicationOrchestrator:
    """Master pipeline execution controller."""

    def __init__(self, resume_path: Optional[str] = None):
        self.resume_path = resume_path or settings.resume_path
        self.repo = JobRepository()
        self.analyzer = ResumeAnalyzer(repo=self.repo)
        self.aggregator = JobSearchAggregator(repo=self.repo)
        self.evaluator = JobEvaluator(repo=self.repo)

    async def run_full_pipeline(self) -> Dict[str, int]:
        """Executes full automated search, evaluation, and application cycle.

        Returns:
            Summary dict of pipeline results.
        """
        logger.info("================ STARTING AGENT PIPELINE CYCLE ================")

        # Step 1: Resume Analysis & Candidate Profile Extraction
        profile = self.analyzer.analyze(self.resume_path)
        logger.info(f"Loaded Profile for Candidate: {profile.full_name or 'Default'}")

        # Step 2: Multi-Source Job Discovery
        discovered = await self.aggregator.execute_discovery_cycle(profile)

        # Step 3: Evaluate Unevaluated Jobs in Database
        unevaluated = self.repo.get_unevaluated_jobs(limit=20)
        logger.info(f"Evaluating {len(unevaluated)} discovered jobs against profile matching threshold...")

        applied_count = 0
        queued_count = 0

        for job in unevaluated:
            eval_result = self.evaluator.evaluate_job(job, profile)
            logger.info(f"Job #{job.id} Score: {eval_result.overall_match_score} -> Decision: {eval_result.decision}")

            if eval_result.decision == "APPLY":
                app = JobApplication(
                    job_id=job.id,
                    status="QUEUED",
                    resume_file_used=self.resume_path,
                    notes=f"Match Score: {eval_result.overall_match_score}. {eval_result.reasoning}"
                )
                self.repo.create_application(app)
                queued_count += 1

        summary = {
            "jobs_discovered": len(discovered),
            "jobs_evaluated": len(unevaluated),
            "applications_queued": queued_count,
        }

        NotificationManager.send_notification(
            "Pipeline Cycle Completed",
            f"Discovered {len(discovered)} jobs. Evaluated {len(unevaluated)}. Queued {queued_count} high-match applications."
        )

        logger.info(f"Pipeline finished: {summary}")
        return summary
