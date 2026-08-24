from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


def _optional_int(value: str | None) -> int | None:
    if value is None or not value.strip():
        return None
    try:
        return int(value)
    except ValueError as exc:
        raise ValueError(f"Se esperaba un entero y se recibió: {value!r}") from exc


def _as_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on", "si", "sí"}


@dataclass(frozen=True, slots=True)
class Settings:
    discord_token: str
    dev_guild_id: int | None = None
    database_path: Path = Path("data/pybot.db")
    log_level: str = "INFO"
    sync_commands: bool = True
    enable_message_content_intent: bool = False
    default_status: str = "Usá /ayuda"
    currency_api_base_url: str = "https://dolarapi.com/v1"
    http_timeout_seconds: float = 8.0

    @classmethod
    def from_env(cls) -> "Settings":
        load_dotenv()

        token = (os.getenv("DISCORD_TOKEN") or os.getenv("DISCORD_KEY") or "").strip()
        if not token:
            raise RuntimeError(
                "Falta DISCORD_TOKEN. Copiá .env.example a .env y configurá el token del bot."
            )

        database_path = Path(os.getenv("DATABASE_PATH", "data/pybot.db")).expanduser()
        timeout_raw = os.getenv("HTTP_TIMEOUT_SECONDS", "8")
        try:
            timeout = float(timeout_raw)
        except ValueError as exc:
            raise ValueError("HTTP_TIMEOUT_SECONDS debe ser numérico") from exc

        return cls(
            discord_token=token,
            dev_guild_id=_optional_int(os.getenv("DEV_GUILD_ID")),
            database_path=database_path,
            log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
            sync_commands=_as_bool(os.getenv("SYNC_COMMANDS"), True),
            enable_message_content_intent=_as_bool(
                os.getenv("ENABLE_MESSAGE_CONTENT_INTENT"), False
            ),
            default_status=os.getenv("BOT_STATUS", "Usá /ayuda").strip() or "Usá /ayuda",
            currency_api_base_url=os.getenv(
                "CURRENCY_API_BASE_URL", "https://dolarapi.com/v1"
            ).rstrip("/"),
            http_timeout_seconds=max(1.0, timeout),
        )
