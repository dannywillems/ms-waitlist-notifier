"""Abstract notifier interface."""

from abc import ABC, abstractmethod
from typing import Any


class Notifier(ABC):
    """Base class for notification backends."""

    @abstractmethod
    async def notify(self, event: str, payload: dict[str, Any]) -> None:
        """Send a notification for the given event."""
