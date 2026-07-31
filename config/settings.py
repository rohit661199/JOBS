"""Configuration management module."""
import os
from pathlib import Path
from typing import Any, Dict, List, Optional
import yaml
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    """Pydantic App Settings combining environment variables and yaml overrides."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True
    )

    # API Keys & LLM settings
    gemini_api_key: Optional[str] = Field(default=None, alias="GEMINI_API_KEY")
    llm_provider: str = Field(default="gemini", alias="LLM_PROVIDER")
    ollama_base_url: str = Field(default="http://localhost:11434", alias="OLLAMA_BASE_URL")
    ollama_model: str = Field(default="llama3.2", alias="OLLAMA_MODEL")

    # Paths & Operational Limits
    match_threshold: int = Field(default=70, alias="MATCH_THRESHOLD")
    daily_application_limit: int = Field(default=20, alias="DAILY_APPLICATION_LIMIT")
    browser_headless: bool = Field(default=False, alias="BROWSER_HEADLESS")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    database_path: str = Field(default="data/jobs_agent.db", alias="DATABASE_PATH")
    resume_path: str = Field(default="resumes/master_resume.pdf", alias="RESUME_PATH")

    # Dynamic YAML configuration settings
    yaml_config_path: str = "config/config.yaml"
    locations: List[str] = ["India", "Bengaluru, India", "Remote"]
    remote_preference: str = "remote_preferred"
    blacklist_companies: List[str] = []
    blacklist_keywords: List[str] = []

    def load_yaml_config(self) -> None:
        """Loads and merges YAML config if file exists."""
        path = Path(self.yaml_config_path)
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}

            # Save explicit fields set in model_fields_set
            explicit_fields = self.model_fields_set

            prefs = data.get("preferences", {})
            if "locations" in prefs and "locations" not in explicit_fields:
                self.locations = prefs["locations"]
            if "remote_preference" in prefs and "remote_preference" not in explicit_fields:
                self.remote_preference = prefs["remote_preference"]
            if "daily_application_limit" in prefs and "daily_application_limit" not in explicit_fields:
                self.daily_application_limit = prefs["daily_application_limit"]

            blacklists = data.get("blacklists", {})
            if "companies" in blacklists and "blacklist_companies" not in explicit_fields:
                self.blacklist_companies = blacklists["companies"]
            if "title_keywords" in blacklists and "blacklist_keywords" not in explicit_fields:
                self.blacklist_keywords = blacklists["title_keywords"]

            matching = data.get("matching", {})
            if "min_score_threshold" in matching and "match_threshold" not in explicit_fields:
                self.match_threshold = matching["min_score_threshold"]

            browser = data.get("browser", {})
            if "headless" in browser and "browser_headless" not in explicit_fields:
                self.browser_headless = browser["headless"]


def get_settings() -> AppSettings:
    """Factory function for retrieving loaded app settings."""
    settings = AppSettings()
    settings.load_yaml_config()
    return settings


settings = get_settings()
