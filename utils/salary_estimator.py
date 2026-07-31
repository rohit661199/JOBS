"""Salary Estimator module providing market rate compensation ranges for Fresher roles in India."""
import re
from typing import Optional


class SalaryEstimator:
    """Estimates market compensation for Fresher (0 years exp) roles in India when unlisted."""

    @staticmethod
    def get_salary_estimate(title: str, company: str, location: str, raw_salary: Optional[str] = None) -> str:
        """Returns listed salary or estimates market salary for Fresher software engineering roles.

        Args:
            title: Job title string.
            company: Hiring company name.
            location: Target geographic location.
            raw_salary: Scraped salary string if available.

        Returns:
            Formatted salary string (e.g., '₹6.5L - ₹10.0L LPA (Estimated)').
        """
        if raw_salary and raw_salary.strip() and raw_salary.strip().lower() not in ["not disclosed", "n/a", "none"]:
            return raw_salary.strip()

        t_lower = title.lower()
        c_lower = company.lower()

        # Product MNCs & Top Tier Tech startups (AI/ML, Systems)
        if any(term in t_lower for term in ["ai", "machine learning", "data engineer", "backend", "full stack"]):
            if any(top in c_lower for top in ["google", "microsoft", "amazon", "flipkart", "swiggy", "zomato", "antigravity"]):
                return "₹14.0L - ₹22.0L LPA (Estimated Tier-1 Fresher CTC)"
            return "₹6.5L - ₹12.0L LPA (Estimated AI/Python Fresher CTC)"

        # Graduate Engineer Trainee / Junior Software Engineer
        if any(term in t_lower for term in ["graduate engineer trainee", "get", "trainee"]):
            return "₹4.5L - ₹7.5L LPA (Estimated GET Fresher CTC)"

        # Default IT / Software Engineer Fresher Market Rate in India
        return "₹5.0L - ₹8.5L LPA (Estimated Fresher Market CTC)"
