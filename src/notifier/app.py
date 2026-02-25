"""FastAPI application for the notifier service."""

import logging
from typing import Any

import uvicorn
from fastapi import Depends, FastAPI

from notifier.config import Settings
from notifier.deps import make_require_api_key
from notifier.mattermost import MattermostNotifier

logger = logging.getLogger(__name__)

settings = Settings()  # type: ignore[call-arg]

notifiers = [
    MattermostNotifier(
        webhook_url=settings.mattermost_webhook_url,
        channel=settings.mattermost_channel,
    ),
]

require_api_key = make_require_api_key(settings)

app = FastAPI(title="Notifier")


@app.get("/health")
async def health() -> dict[str, str]:
    """Health check."""
    return {"status": "ok"}


@app.post("/notify/waitlist")
async def notify_waitlist(
    payload: dict[str, Any],
    _auth: None = Depends(require_api_key),
) -> dict[str, str]:
    """Dispatch a waitlist signup notification."""
    for notifier in notifiers:
        try:
            await notifier.notify("waitlist", payload)
        except Exception:
            logger.exception("Notifier %s failed", type(notifier).__name__)
    return {"status": "ok"}


def main() -> None:
    """Entry point for the notifier service."""
    uvicorn.run(app, host="0.0.0.0", port=8002)
