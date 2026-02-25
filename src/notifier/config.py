"""Configuration loaded from environment variables."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Notifier service settings."""

    mattermost_webhook_url: str
    mattermost_channel: str = ""
    notify_api_key: str
    scribe_dashboard_url: str = ""
