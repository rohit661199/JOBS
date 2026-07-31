"""Playwright browser driver manager supplying persistent contexts and stealth defaults."""
from pathlib import Path
from typing import Optional
from playwright.async_api import Browser, BrowserContext, Page, async_playwright
from config.settings import settings
from browser.session import SessionManager
from utils.logger import logger


class PlaywrightDriver:
    """Manages Async Playwright browser lifecycle and persistent contexts."""

    def __init__(self, headless: Optional[bool] = None):
        self.headless = settings.browser_headless if headless is None else headless
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.session_mgr = SessionManager()

    async def start(self, platform_name: str = "default") -> Page:
        """Launches Playwright Chromium browser instance with session restoration.

        Returns:
            Playwright Page instance.
        """
        logger.info(f"Initializing Playwright browser context (Headless: {self.headless})...")
        self.playwright = await async_playwright().start()

        state_file = self.session_mgr.get_state_file_path(platform_name)
        storage_state = str(state_file) if state_file.exists() else None

        if storage_state:
            logger.info(f"Restoring session state from: {state_file}")

        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            slow_mo=100,
            args=["--no-sandbox", "--disable-setuid-sandbox"]
        )

        self.context = await self.browser.new_context(
            storage_state=storage_state,
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        page = await self.context.new_page()
        page.set_default_timeout(30000)
        return page

    async def close(self, platform_name: str = "default") -> None:
        """Saves storage state and terminates browser instance."""
        if self.context:
            try:
                await self.session_mgr.save_storage_state(self.context, platform_name)
                await self.context.close()
            except Exception as e:
                logger.debug(f"Error closing browser context: {e}")

        if self.browser:
            await self.browser.close()

        if self.playwright:
            await self.playwright.stop()
        logger.info("Playwright driver shutdown completed.")
