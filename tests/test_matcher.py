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
    # Expected: (80*0.25) + (90*0.25) + (70*0.20) + (85*0.15) + (75*0.15)
    # = 20 + 22.5 + 14 + 12.75 + 11.25 = 80.5
    assert score == 80.5


def test_decision_engine_blacklist():
    """Tests decision engine rejecting blacklisted companies."""
    engine = DecisionEngine()
    job = JobListing(
        title="Software Developer",
        company="Revature Inc",
        location="Remote",
        source_url="http://example.com/revature",
        source_platform="Indeed",
        raw_description="Developer position.",
        fingerprint="fp_revature"
    )
    profile = CandidateProfile(raw_text_hash="dummy_hash")

    decision, reasoning = engine.evaluate_decision(95.0, job, profile, "High score")
    assert decision == "REJECT"
    assert "blacklist" in reasoning.lower()
