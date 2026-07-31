"""Unit tests for SalaryEstimator module."""
import pytest
from utils.salary_estimator import SalaryEstimator


def test_salary_estimator_with_none_and_nan():
    """Tests that SalaryEstimator handles None and float NaN values gracefully."""
    est_none = SalaryEstimator.get_salary_estimate("Python Developer", "Tech", "Bengaluru", None)
    assert "LPA" in est_none

    import numpy as np
    est_nan = SalaryEstimator.get_salary_estimate("Python Developer", "Tech", "Bengaluru", np.nan)
    assert "LPA" in est_nan


def test_salary_estimator_valid_string():
    """Tests returning actual raw salary when available."""
    est = SalaryEstimator.get_salary_estimate("Python Developer", "Tech", "Bengaluru", "₹12.0L LPA")
    assert est == "₹12.0L LPA"
