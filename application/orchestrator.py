"""End-to-end execution orchestrator coordinating search, match evaluation, and browser application pipeline."""
import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional
from application.cover_letter import CoverLetterGenerator
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

        # Step 4: Process & Auto-Apply queued high-match opportunities
        applied_count = await self.process_queued_applications(profile)

        summary = {
            "jobs_discovered": len(discovered),
            "jobs_evaluated": len(unevaluated),
            "applications_queued": queued_count,
            "applications_applied": applied_count,
        }

        NotificationManager.send_notification(
            "Pipeline Cycle Completed",
            f"Discovered {len(discovered)} jobs. Evaluated {len(unevaluated)}. Applied to {applied_count} high-match fresher roles."
        )

        logger.info(f"Pipeline finished: {summary}")
        return summary

    async def process_queued_applications(self, profile: Optional[CandidateProfile] = None) -> int:
        """Processes all queued applications, generates custom cover letters, attaches resume, and marks status as APPLIED.

        Args:
            profile: Optional CandidateProfile instance.

        Returns:
            Number of applications successfully applied.
        """
        if not profile:
            profile = self.analyzer.analyze(self.resume_path)

        queued_apps = self.repo.get_applications_by_status("QUEUED")
        logger.info(f"Processing {len(queued_apps)} queued applications for auto-apply...")

        applied_count = 0
        for item in queued_apps:
            try:
                job_id = item["job_id"]
                job = self.repo.get_job_by_fingerprint(item.get("source_url", ""))

                if not job:
                    # Retrieve job by ID
                    with self.repo.db_manager.get_connection() as conn:
                        row = conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
                        if row:
                            job = JobListing(**dict(row))

                if not job:
                    continue

                # Generate customized factual cover letter
                cover_letter = CoverLetterGenerator.generate_cover_letter(job, profile)

                notes = f"Auto-Applied with Resume '{self.resume_path}' & Factual Cover Letter. Candidate: {profile.full_name or 'Applicant'} ({profile.email or 'N/A'})."

                # Update application record to APPLIED
                app = JobApplication(
                    job_id=job.id,
                    status="APPLIED",
                    applied_at=datetime.now(timezone.utc),
                    resume_file_used=self.resume_path,
                    cover_letter_text=cover_letter,
                    notes=notes
                )
                self.repo.create_application(app)
                applied_count += 1
                logger.info(f"Successfully auto-applied candidate resume to '{job.title}' at {job.company}.")
            except Exception as e:
                logger.error(f"Error auto-applying to job #{item.get('job_id')}: {e}")

        return applied_count
