"""Unit tests for MatchScorer and DecisionEngine."""
import pytest
from database.models import CandidateProfile, JobListing
from matcher.decision_engine import DecisionEngine
from matcher.scoring import MatchScorer


def test_calculate_overall_score():
    """Tests weighted scoring matrix."""
    score = MatchScorer.calculate_overall_score(
        skills_score=80.0,
        tech_stack_score=90.0,
        experience_score=70.0,
        domain_score=85.0,
        ats_keyword_score=75.0,
    )
    assert score == 80.5


def test_decision_engine_blacklist():
    """Tests decision engine rejecting blacklisted companies."""
    engine = DecisionEngine()
    job = JobListing(
        title="Junior Developer",
        company="Revature Inc",
        location="Remote",
        source_url="http://example.com/revature",
        source_platform="Indeed",
        raw_description="Developer position for freshers.",
        fingerprint="fp_revature"
    )
    profile = CandidateProfile(raw_text_hash="dummy_hash")

    decision, reasoning = engine.evaluate_decision(95.0, job, profile, "High score")
    assert decision == "REJECT"
    assert "blacklist" in reasoning.lower()


def test_decision_engine_reject_high_experience_for_freshers():
    """Tests that senior roles requiring 5+ years experience are rejected for freshers."""
    engine = DecisionEngine()
    job = JobListing(
        title="Senior Python Architect",
        company="Global Software LLC",
        location="Remote",
        source_url="http://example.com/senior_job",
        source_platform="LinkedIn",
        raw_description="Requires 5+ years of experience in system architecture.",
        fingerprint="fp_senior_job"
    )
    profile = CandidateProfile(raw_text_hash="dummy_hash")

    decision, reasoning = engine.evaluate_decision(95.0, job, profile, "High score")
    assert decision == "REJECT"
    assert "fresher" in reasoning.lower() or "experience" in reasoning.lower()
