"""Notification dispatch manager for desktop alerts and console logging."""
from typing import Optional
from config.settings import settings
from utils.logger import logger

try:
    from plyer import notification
    PLYER_AVAILABLE = True
except ImportError:
    PLYER_AVAILABLE = False


class NotificationManager:
    """Dispatches desktop notifications for HITL events and status milestones."""

    @staticmethod
    def send_notification(title: str, message: str, is_warning: bool = False) -> None:
        """Sends desktop notification safely and logs to console.

        Args:
            title: Alert title string.
            message: Alert description body.
            is_warning: High priority indicator.
        """
        log_fn = logger.warning if is_warning else logger.info
        log_fn(f"[NOTIFICATION] {title}: {message}")

        if settings.yaml_config_path and PLYER_AVAILABLE:
            try:
                notification.notify(
                    title=f"Job Agent: {title}",
                    message=message[:200],
                    app_name="Autonomous Job Agent",
                    timeout=5
                )
            except Exception as e:
                logger.debug(f"Desktop notification skipped: {e}")
