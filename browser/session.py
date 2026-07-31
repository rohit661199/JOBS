"""Browser session and cookie storage state manager."""
from pathlib import Path
from playwright.async_api import BrowserContext
from utils.logger import logger


class SessionManager:
    """Manages persistent browser storage states for automatic login persistence."""

    def __init__(self, storage_dir: str = "data/browser_sessions"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def get_state_file_path(self, platform_name: str) -> Path:
        """Returns JSON storage state file path for platform."""
        clean_name = platform_name.lower().replace(" ", "_")
        return self.storage_dir / f"{clean_name}_state.json"

    async def save_storage_state(self, context: BrowserContext, platform_name: str) -> None:
        """Saves current browser cookies and storage state to JSON."""
        state_file = self.get_state_file_path(platform_name)
        await context.storage_state(path=str(state_file))
        logger.info(f"Saved persistent session state for {platform_name} to {state_file}")
