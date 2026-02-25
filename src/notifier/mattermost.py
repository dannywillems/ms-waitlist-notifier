"""Mattermost webhook notifier."""

import logging
from typing import Any

import httpx

from notifier.base import Notifier

logger = logging.getLogger(__name__)


class MattermostNotifier(Notifier):
    """Send notifications via a Mattermost incoming webhook."""

    def __init__(
        self,
        webhook_url: str,
        channel: str = "",
    ) -> None:
        self.webhook_url = webhook_url
        self.channel = channel

    async def notify(self, event: str, payload: dict[str, Any]) -> None:
        """Post a message to the configured Mattermost webhook."""
        text = self._format(event, payload)
        body: dict[str, str] = {"text": text}
        if self.channel:
            body["channel"] = self.channel

        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(self.webhook_url, json=body)
            resp.raise_for_status()

    def _format(self, event: str, payload: dict[str, Any]) -> str:
        email = payload.get("email", "unknown")
        timestamp = payload.get("timestamp", "unknown")
        return f"New waitlist signup: {email} at {timestamp}"
