"""Human-In-The-Loop (HITL) Safety Guard detecting security challenges and manual intervention triggers."""
from playwright.async_api import Page
from notifications.notifier import NotificationManager
from utils.logger import logger


class HITLGuard:
    """Monitors Playwright page for CAPTCHAs, OTPs, identity verifications, and custom assessments."""

    SECURITY_SELECTORS = [
        "iframe[src*='recaptcha']",
        "iframe[src*='hcaptcha']",
        "iframe[src*='challenges.cloudflare.com']",
        "input[name*='otp']",
        "input[id*='verification_code']",
        "div:has-text('Security Check')",
        "div:has-text('Verify you are human')",
        "div:has-text('Enter verification code')",
    ]

    @classmethod
    async def check_security_barriers(cls, page: Page) -> bool:
        """Inspects current page state for security challenges requiring human intervention.

        Returns:
            True if security challenge detected, False if safe to proceed.
        """
        for selector in cls.SECURITY_SELECTORS:
            try:
                element = await page.query_selector(selector)
                if element and await element.is_visible():
                    logger.warning(f"HITL Safety Barrier Triggered: Detected element matching '{selector}'")
                    return True
            except Exception:
                continue
        return False

    @classmethod
    async def handle_hitl_pause(cls, page: Page, reason: str = "Security barrier encountered") -> None:
        """Pauses automation, sends desktop notification, and waits for user terminal confirmation."""
        msg = f"{reason}. Automation paused. Please solve the challenge in the open browser window."
        logger.warning(f"=== HUMAN-IN-THE-LOOP REQUIRED ===\n{msg}")
        NotificationManager.send_notification("Action Required", msg, is_warning=True)

        print("\n" + "=" * 60)
        print(" [PAUSED FOR HUMAN INTERVENTION]")
        print(f" Reason: {reason}")
        print(" Please complete the required action in the browser window.")
        print(" Press ENTER in this console when you are ready to continue...")
        print("=" * 60 + "\n")

        input()
        logger.info("Resuming automation post human confirmation.")
