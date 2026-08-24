from datetime import UTC, datetime, timedelta

import pytest

from pybot.database import Database


@pytest.mark.asyncio
async def test_guild_settings_roundtrip(tmp_path) -> None:
    database = Database(tmp_path / "pybot.db")
    await database.connect()
    try:
        initial = await database.get_guild_settings(100)
        assert initial.guild_id == 100
        assert initial.welcome_channel_id is None

        await database.update_guild_setting(100, "welcome_channel_id", 200)
        await database.update_guild_setting(100, "autorole_id", 300)

        updated = await database.get_guild_settings(100)
        assert updated.welcome_channel_id == 200
        assert updated.autorole_id == 300
    finally:
        await database.close()


@pytest.mark.asyncio
async def test_reminders_are_persistent_and_deletable(tmp_path) -> None:
    database = Database(tmp_path / "pybot.db")
    await database.connect()
    try:
        due_at = datetime.now(UTC) + timedelta(minutes=5)
        reminder_id = await database.add_reminder(
            user_id=1,
            channel_id=2,
            guild_id=3,
            remind_at=due_at,
            message="Revisar el deploy",
        )

        reminders = await database.list_user_reminders(1)
        assert len(reminders) == 1
        assert reminders[0].id == reminder_id
        assert reminders[0].message == "Revisar el deploy"

        assert await database.delete_reminder(reminder_id, user_id=999) is False
        assert await database.delete_reminder(reminder_id, user_id=1) is True
        assert await database.list_user_reminders(1) == []
    finally:
        await database.close()


@pytest.mark.asyncio
async def test_due_reminders_only_returns_expired_items(tmp_path) -> None:
    database = Database(tmp_path / "pybot.db")
    await database.connect()
    try:
        now = datetime.now(UTC)
        await database.add_reminder(
            user_id=1,
            channel_id=2,
            guild_id=None,
            remind_at=now - timedelta(seconds=1),
            message="Vencido",
        )
        await database.add_reminder(
            user_id=1,
            channel_id=2,
            guild_id=None,
            remind_at=now + timedelta(hours=1),
            message="Futuro",
        )

        due = await database.get_due_reminders(now)
        assert [item.message for item in due] == ["Vencido"]
    finally:
        await database.close()
