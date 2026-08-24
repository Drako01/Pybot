from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

import aiosqlite


@dataclass(slots=True)
class GuildSettings:
    guild_id: int
    welcome_channel_id: int | None = None
    farewell_channel_id: int | None = None
    modlog_channel_id: int | None = None
    autorole_id: int | None = None


@dataclass(slots=True)
class Reminder:
    id: int
    user_id: int
    channel_id: int
    guild_id: int | None
    remind_at: datetime
    message: str


class Database:
    def __init__(self, path: Path) -> None:
        self.path = path
        self._connection: aiosqlite.Connection | None = None

    async def connect(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._connection = await aiosqlite.connect(self.path)
        self._connection.row_factory = aiosqlite.Row
        await self._connection.execute("PRAGMA journal_mode=WAL")
        await self._connection.execute("PRAGMA foreign_keys=ON")
        await self._create_schema()

    async def close(self) -> None:
        if self._connection is not None:
            await self._connection.close()
            self._connection = None

    @property
    def connection(self) -> aiosqlite.Connection:
        if self._connection is None:
            raise RuntimeError("La base de datos todavía no fue inicializada")
        return self._connection

    async def _create_schema(self) -> None:
        await self.connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS guild_settings (
                guild_id INTEGER PRIMARY KEY,
                welcome_channel_id INTEGER,
                farewell_channel_id INTEGER,
                modlog_channel_id INTEGER,
                autorole_id INTEGER,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                channel_id INTEGER NOT NULL,
                guild_id INTEGER,
                remind_at TEXT NOT NULL,
                message TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS self_roles (
                guild_id INTEGER NOT NULL,
                role_id INTEGER NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (guild_id, role_id)
            );

            CREATE INDEX IF NOT EXISTS idx_reminders_due ON reminders(remind_at);
            CREATE INDEX IF NOT EXISTS idx_reminders_user ON reminders(user_id);
            CREATE INDEX IF NOT EXISTS idx_self_roles_guild ON self_roles(guild_id);
            """
        )
        await self.connection.commit()

    async def get_guild_settings(self, guild_id: int) -> GuildSettings:
        cursor = await self.connection.execute(
            "SELECT * FROM guild_settings WHERE guild_id = ?", (guild_id,)
        )
        row = await cursor.fetchone()
        await cursor.close()

        if row is None:
            return GuildSettings(guild_id=guild_id)

        return GuildSettings(
            guild_id=row["guild_id"],
            welcome_channel_id=row["welcome_channel_id"],
            farewell_channel_id=row["farewell_channel_id"],
            modlog_channel_id=row["modlog_channel_id"],
            autorole_id=row["autorole_id"],
        )

    async def update_guild_setting(self, guild_id: int, field: str, value: int | None) -> None:
        allowed_fields = {
            "welcome_channel_id",
            "farewell_channel_id",
            "modlog_channel_id",
            "autorole_id",
        }
        if field not in allowed_fields:
            raise ValueError(f"Campo de configuración no permitido: {field}")

        await self.connection.execute(
            "INSERT INTO guild_settings (guild_id) VALUES (?) "
            "ON CONFLICT(guild_id) DO NOTHING",
            (guild_id,),
        )
        await self.connection.execute(
            f"UPDATE guild_settings SET {field} = ?, updated_at = CURRENT_TIMESTAMP "
            "WHERE guild_id = ?",
            (value, guild_id),
        )
        await self.connection.commit()

    async def add_self_role(self, guild_id: int, role_id: int) -> None:
        await self.connection.execute(
            "INSERT OR IGNORE INTO self_roles (guild_id, role_id) VALUES (?, ?)",
            (guild_id, role_id),
        )
        await self.connection.commit()

    async def remove_self_role(self, guild_id: int, role_id: int) -> bool:
        cursor = await self.connection.execute(
            "DELETE FROM self_roles WHERE guild_id = ? AND role_id = ?",
            (guild_id, role_id),
        )
        await self.connection.commit()
        deleted = cursor.rowcount > 0
        await cursor.close()
        return deleted

    async def list_self_roles(self, guild_id: int) -> list[int]:
        cursor = await self.connection.execute(
            "SELECT role_id FROM self_roles WHERE guild_id = ? ORDER BY role_id",
            (guild_id,),
        )
        rows = await cursor.fetchall()
        await cursor.close()
        return [int(row["role_id"]) for row in rows]

    async def add_reminder(
        self,
        *,
        user_id: int,
        channel_id: int,
        guild_id: int | None,
        remind_at: datetime,
        message: str,
    ) -> int:
        cursor = await self.connection.execute(
            """
            INSERT INTO reminders (user_id, channel_id, guild_id, remind_at, message)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                user_id,
                channel_id,
                guild_id,
                remind_at.astimezone(UTC).isoformat(),
                message,
            ),
        )
        await self.connection.commit()
        reminder_id = cursor.lastrowid
        await cursor.close()
        if reminder_id is None:
            raise RuntimeError("No fue posible crear el recordatorio")
        return reminder_id

    async def get_due_reminders(self, now: datetime) -> list[Reminder]:
        cursor = await self.connection.execute(
            "SELECT * FROM reminders WHERE remind_at <= ? ORDER BY remind_at ASC LIMIT 100",
            (now.astimezone(UTC).isoformat(),),
        )
        rows = await cursor.fetchall()
        await cursor.close()
        return [self._row_to_reminder(row) for row in rows]

    async def list_user_reminders(self, user_id: int, limit: int = 10) -> list[Reminder]:
        cursor = await self.connection.execute(
            "SELECT * FROM reminders WHERE user_id = ? ORDER BY remind_at ASC LIMIT ?",
            (user_id, limit),
        )
        rows = await cursor.fetchall()
        await cursor.close()
        return [self._row_to_reminder(row) for row in rows]

    async def delete_reminder(self, reminder_id: int, user_id: int | None = None) -> bool:
        if user_id is None:
            cursor = await self.connection.execute(
                "DELETE FROM reminders WHERE id = ?", (reminder_id,)
            )
        else:
            cursor = await self.connection.execute(
                "DELETE FROM reminders WHERE id = ? AND user_id = ?",
                (reminder_id, user_id),
            )
        await self.connection.commit()
        deleted = cursor.rowcount > 0
        await cursor.close()
        return deleted

    @staticmethod
    def _row_to_reminder(row: aiosqlite.Row) -> Reminder:
        return Reminder(
            id=row["id"],
            user_id=row["user_id"],
            channel_id=row["channel_id"],
            guild_id=row["guild_id"],
            remind_at=datetime.fromisoformat(row["remind_at"]).astimezone(UTC),
            message=row["message"],
        )
