"""Repository pattern implementation for jobs, candidate profiles, evaluations, and applications."""
import json
import sqlite3
from datetime import datetime
from typing import Any, Dict, List, Optional
from database.connection import DatabaseManager, get_db
from database.models import CandidateProfile, JobApplication, JobEvaluation, JobListing
from utils.logger import logger


class JobRepository:
    """Handles CRUD operations for job listings, evaluations, and applications."""

    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        self.db_manager = db_manager or get_db()

    # --- Candidate Profile ---
    def save_candidate_profile(self, profile: CandidateProfile) -> int:
        """Saves candidate profile extraction to database."""
        sql = """
        INSERT INTO candidate_profiles (raw_text_hash, profile_json)
        VALUES (?, ?)
        ON CONFLICT(raw_text_hash) DO UPDATE SET
            profile_json = excluded.profile_json;
        """
        profile_json_str = profile.model_dump_json()
        with self.db_manager.get_connection() as conn:
            cursor = conn.execute(sql, (profile.raw_text_hash, profile_json_str))
            conn.commit()
            return cursor.lastrowid

    def get_candidate_profile_by_hash(self, raw_hash: str) -> Optional[CandidateProfile]:
        """Retrieves profile matching the raw resume text hash."""
        sql = "SELECT profile_json FROM candidate_profiles WHERE raw_text_hash = ?"
        with self.db_manager.get_connection() as conn:
            row = conn.execute(sql, (raw_hash,)).fetchone()
            if row:
                return CandidateProfile.model_validate_json(row["profile_json"])
        return None

    # --- Job Listing ---
    def add_job(self, job: JobListing) -> Optional[int]:
        """Inserts a discovered job posting into the database. Returns job ID or None if duplicate."""
        sql = """
        INSERT OR IGNORE INTO jobs (title, company, location, source_url, source_platform, raw_description, salary_range, employment_type, posted_date, fingerprint)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.execute(sql, (
                    job.title, job.company, job.location, job.source_url,
                    job.source_platform, job.raw_description, job.salary_range,
                    job.employment_type, job.posted_date, job.fingerprint
                ))
                conn.commit()
                if cursor.lastrowid and cursor.lastrowid > 0:
                    logger.info(f"Saved new job: '{job.title}' at {job.company}")
                    return cursor.lastrowid
                else:
                    logger.debug(f"Duplicate job skipped: {job.title} at {job.company}")
                    return None
        except sqlite3.IntegrityError as e:
            logger.debug(f"Duplicate job integrity catch: {job.title} - {e}")
            return None

    def get_job_by_fingerprint(self, fingerprint: str) -> Optional[JobListing]:
        """Fetches job listing by fingerprint hash."""
        sql = "SELECT * FROM jobs WHERE fingerprint = ?"
        with self.db_manager.get_connection() as conn:
            row = conn.execute(sql, (fingerprint,)).fetchone()
            if row:
                return JobListing(**dict(row))
        return None

    def get_unevaluated_jobs(self, limit: int = 50) -> List[JobListing]:
        """Fetches jobs that have not yet been evaluated by LLM Matcher."""
        sql = """
        SELECT j.* FROM jobs j
        LEFT JOIN job_evaluations e ON j.id = e.job_id
        WHERE e.id IS NULL
        LIMIT ?
        """
        with self.db_manager.get_connection() as conn:
            rows = conn.execute(sql, (limit,)).fetchall()
            return [JobListing(**dict(row)) for row in rows]

    # --- Job Evaluations ---
    def save_evaluation(self, eval_data: JobEvaluation) -> int:
        """Saves evaluation and scoring decision for a job."""
        sql = """
        INSERT INTO job_evaluations (job_id, overall_match_score, skills_score, tech_stack_score, experience_score, domain_score, ats_keyword_score, strengths, weaknesses, reasoning, decision)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(job_id) DO UPDATE SET
            overall_match_score = excluded.overall_match_score,
            skills_score = excluded.skills_score,
            tech_stack_score = excluded.tech_stack_score,
            experience_score = excluded.experience_score,
            domain_score = excluded.domain_score,
            ats_keyword_score = excluded.ats_keyword_score,
            strengths = excluded.strengths,
            weaknesses = excluded.weaknesses,
            reasoning = excluded.reasoning,
            decision = excluded.decision,
            evaluated_at = CURRENT_TIMESTAMP;
        """
        with self.db_manager.get_connection() as conn:
            cursor = conn.execute(sql, (
                eval_data.job_id, eval_data.overall_match_score, eval_data.skills_score,
                eval_data.tech_stack_score, eval_data.experience_score, eval_data.domain_score,
                eval_data.ats_keyword_score, json.dumps(eval_data.strengths),
                json.dumps(eval_data.weaknesses), eval_data.reasoning, eval_data.decision
            ))
            conn.commit()
            return cursor.lastrowid

    # --- Applications ---
    def create_application(self, app_data: JobApplication) -> int:
        """Creates or updates application tracking status."""
        sql = """
        INSERT INTO applications (job_id, status, applied_at, resume_file_used, cover_letter_text, notes)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(job_id) DO UPDATE SET
            status = excluded.status,
            applied_at = excluded.applied_at,
            cover_letter_text = excluded.cover_letter_text,
            notes = excluded.notes,
            updated_at = CURRENT_TIMESTAMP;
        """
        applied_at_str = app_data.applied_at.isoformat() if app_data.applied_at else None
        with self.db_manager.get_connection() as conn:
            cursor = conn.execute(sql, (
                app_data.job_id, app_data.status, applied_at_str,
                app_data.resume_file_used, app_data.cover_letter_text, app_data.notes
            ))
            conn.commit()
            return cursor.lastrowid

    def get_applications_by_status(self, status: str) -> List[Dict[str, Any]]:
        """Returns applications joined with job info filtered by status."""
        sql = """
        SELECT a.id as app_id, a.status, a.applied_at, j.title, j.company, j.location, j.source_url, e.overall_match_score
        FROM applications a
        JOIN jobs j ON a.job_id = j.id
        JOIN job_evaluations e ON j.id = e.job_id
        WHERE a.status = ?
        ORDER BY a.created_at DESC
        """
        with self.db_manager.get_connection() as conn:
            rows = conn.execute(sql, (status,)).fetchall()
            return [dict(row) for row in rows]

    def get_analytics_summary(self) -> Dict[str, Any]:
        """Calculates operational analytics for Streamlit Dashboard."""
        sql_counts = """
        SELECT
            (SELECT COUNT(*) FROM jobs) as total_jobs_found,
            (SELECT COUNT(*) FROM job_evaluations WHERE decision = 'APPLY') as high_match_jobs,
            (SELECT COUNT(*) FROM applications WHERE status = 'APPLIED') as total_applied,
            (SELECT COUNT(*) FROM applications WHERE status = 'HITL_PAUSED') as pending_hitl,
            (SELECT COUNT(*) FROM applications WHERE status = 'INTERVIEW') as interviews
        """
        with self.db_manager.get_connection() as conn:
            row = conn.execute(sql_counts).fetchone()
            return dict(row) if row else {}
