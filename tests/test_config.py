"""Unit tests for configuration loading."""
import pytest
from config.settings import AppSettings, get_settings


def test_settings_load():
    """Tests loading defaults and settings instantiation."""
    settings = get_settings()
    assert settings.match_threshold is not None
    assert settings.database_path is not None
    assert isinstance(settings.locations, list)


def test_custom_settings_override():
    """Tests Pydantic custom overrides."""
    s = AppSettings(match_threshold=85, llm_provider="ollama")
    assert s.match_threshold == 85
    assert s.llm_provider == "ollama"
