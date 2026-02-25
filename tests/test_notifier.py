"""Tests for the notifier micro-service."""

from typing import Any
from unittest.mock import AsyncMock, patch

import httpx
import pytest
from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def _set_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Set required environment variables before importing the app."""
    monkeypatch.setenv(
        "MATTERMOST_WEBHOOK_URL", "https://mm.example.com/hooks/abc"
    )
    monkeypatch.setenv("NOTIFY_API_KEY", "test-key")


@pytest.fixture()
def client(_set_env: None) -> TestClient:
    """Create a test client with env vars set."""
    # Import inside fixture so env vars are available at module load
    from notifier.app import app

    return TestClient(app)


AUTH = {"Authorization": "Bearer test-key"}


class TestHealth:
    def test_health(self, client: TestClient) -> None:
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}


class TestAuth:
    def test_missing_auth(self, client: TestClient) -> None:
        resp = client.post("/notify/waitlist", json={"email": "a@b.com"})
        assert resp.status_code == 422

    def test_invalid_auth(self, client: TestClient) -> None:
        resp = client.post(
            "/notify/waitlist",
            json={"email": "a@b.com"},
            headers={"Authorization": "Bearer wrong"},
        )
        assert resp.status_code == 401

    def test_valid_auth_dispatches(self, client: TestClient) -> None:
        with patch("notifier.app.notifiers", []):
            resp = client.post(
                "/notify/waitlist",
                json={"email": "a@b.com"},
                headers=AUTH,
            )
            assert resp.status_code == 200
            assert resp.json() == {"status": "ok"}


def _ok_response() -> httpx.Response:
    """Build a minimal httpx.Response(200) with a request attached."""
    req = httpx.Request("POST", "https://mm.example.com/hooks/abc")
    return httpx.Response(200, request=req)


class TestMattermostNotifier:
    @pytest.mark.asyncio
    async def test_notify_posts_to_webhook(self) -> None:
        from notifier.mattermost import MattermostNotifier

        notifier = MattermostNotifier(
            webhook_url="https://mm.example.com/hooks/abc",
            channel="town-square",
        )

        with patch("notifier.mattermost.httpx.AsyncClient") as mock_cls:
            mock_client = AsyncMock()
            mock_client.post.return_value = _ok_response()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_cls.return_value = mock_client

            await notifier.notify(
                "waitlist",
                {
                    "email": "test@example.com",
                    "timestamp": "2026-02-25T12:00:00",
                },
            )

            mock_client.post.assert_called_once()
            call_args: Any = mock_client.post.call_args
            assert call_args[0][0] == "https://mm.example.com/hooks/abc"
            body = call_args[1]["json"]
            assert "test@example.com" in body["text"]
            assert body["channel"] == "town-square"

    @pytest.mark.asyncio
    async def test_notify_without_channel(self) -> None:
        from notifier.mattermost import MattermostNotifier

        notifier = MattermostNotifier(
            webhook_url="https://mm.example.com/hooks/abc",
        )

        with patch("notifier.mattermost.httpx.AsyncClient") as mock_cls:
            mock_client = AsyncMock()
            mock_client.post.return_value = _ok_response()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_cls.return_value = mock_client

            await notifier.notify("waitlist", {"email": "x@y.com"})

            body: Any = mock_client.post.call_args[1]["json"]
            assert "channel" not in body


class TestDispatch:
    def test_notifier_failure_does_not_break_endpoint(
        self, client: TestClient
    ) -> None:
        """A failing notifier should not cause a 500."""
        from notifier.mattermost import MattermostNotifier

        broken = MattermostNotifier(
            webhook_url="https://mm.example.com/hooks/abc"
        )

        with patch("notifier.app.notifiers", [broken]):
            with patch.object(
                broken, "notify", side_effect=Exception("webhook down")
            ):
                resp = client.post(
                    "/notify/waitlist",
                    json={"email": "a@b.com"},
                    headers=AUTH,
                )
                assert resp.status_code == 200
