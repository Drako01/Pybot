from pathlib import Path

import pytest

from pybot.config import Settings


def test_settings_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DISCORD_TOKEN", "test-token")
    monkeypatch.setenv("DEV_GUILD_ID", "123456")
    monkeypatch.setenv("DATABASE_PATH", "data/test.db")
    monkeypatch.setenv("SYNC_COMMANDS", "false")
    monkeypatch.setenv("ENABLE_MESSAGE_CONTENT_INTENT", "true")
    monkeypatch.setenv("HTTP_TIMEOUT_SECONDS", "4.5")

    settings = Settings.from_env()

    assert settings.discord_token == "test-token"
    assert settings.dev_guild_id == 123456
    assert settings.database_path == Path("data/test.db")
    assert settings.sync_commands is False
    assert settings.enable_message_content_intent is True
    assert settings.http_timeout_seconds == 4.5


def test_settings_requires_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DISCORD_TOKEN", raising=False)
    monkeypatch.delenv("DISCORD_KEY", raising=False)

    with pytest.raises(RuntimeError, match="DISCORD_TOKEN"):
        Settings.from_env()
