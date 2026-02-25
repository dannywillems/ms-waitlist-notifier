"""FastAPI authentication dependencies."""

from collections.abc import Callable, Coroutine

from fastapi import Header, HTTPException

from notifier.config import Settings


def make_require_api_key(
    settings: Settings,
) -> Callable[..., Coroutine[None, None, None]]:
    """Create an API key dependency bound to the given settings."""

    async def require_api_key(
        authorization: str = Header(...),
    ) -> None:
        scheme, _, token = authorization.partition(" ")
        if scheme.lower() != "bearer" or token != settings.notify_api_key:
            raise HTTPException(status_code=401, detail="Invalid API key")

    return require_api_key
