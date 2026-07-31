"""Unit tests for SQLite database connection and repository layer."""
import os
import tempfile
import pytest
from database.connection import DatabaseManager
from database.models import CandidateProfile, JobListing, JobEvaluation
from database.repository import JobRepository


@pytest.fixture
def temp_repo():
    """Fixture supplying an isolated in-memory or temporary sqlite database."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tf:
        temp_db_path = tf.name

    db_manager = DatabaseManager(db_path=temp_db_path)
    repo = JobRepository(db_manager=db_manager)
    yield repo

    # Teardown
    if os.path.exists(temp_db_path):
        try:
            os.remove(temp_db_path)
        except PermissionError:
            pass


def test_add_and_retrieve_job(temp_repo):
    """Tests saving and checking duplicate job listings."""
    job = JobListing(
        title="Senior AI Agent Engineer",
        company="Antigravity Corp",
        location="Remote",
        source_url="https://example.com/jobs/123",
        source_platform="LinkedIn",
        raw_description="Build autonomous agents using Python and Gemini.",
        fingerprint="antigravity_ai_engineer_123"
    )

    job_id = temp_repo.add_job(job)
    assert job_id is not None
    assert job_id > 0

    # Test duplicate insertion prevention
    dup_id = temp_repo.add_job(job)
    assert dup_id is None


def test_candidate_profile_persistence(temp_repo):
    """Tests saving candidate profile JSON."""
    profile = CandidateProfile(
        full_name="Jane Doe",
        email="jane@example.com",
        programming_languages=["Python", "TypeScript"],
        raw_text_hash="hash_123456"
    )

    row_id = temp_repo.save_candidate_profile(profile)
    assert row_id is not None

    retrieved = temp_repo.get_candidate_profile_by_hash("hash_123456")
    assert retrieved is not None
    assert retrieved.full_name == "Jane Doe"
    assert "Python" in retrieved.programming_languages
