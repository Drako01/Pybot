from __future__ import annotations

import logging
from typing import Final

import aiohttp
import discord
from discord import app_commands
from discord.ext import commands

from pybot.config import Settings
from pybot.database import Database


LOGGER = logging.getLogger("pybot")
EXTENSIONS: Final[tuple[str, ...]] = (
    "pybot.cogs.core",
    "pybot.cogs.community",
    "pybot.cogs.moderation",
    "pybot.cogs.utilities",
    "pybot.cogs.reminders",
)


class PyBot(commands.Bot):
    def __init__(self, settings: Settings) -> None:
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = settings.enable_message_content_intent

        super().__init__(
            command_prefix=commands.when_mentioned_or("!"),
            intents=intents,
            help_command=None,
            case_insensitive=True,
            allowed_mentions=discord.AllowedMentions(
                everyone=False,
                roles=False,
                replied_user=False,
            ),
        )

        self.settings = settings
        self.database = Database(settings.database_path)
        self.http_session: aiohttp.ClientSession | None = None
        self.tree.on_error = self._on_app_command_error

    async def setup_hook(self) -> None:
        await self.database.connect()
        timeout = aiohttp.ClientTimeout(total=self.settings.http_timeout_seconds)
        self.http_session = aiohttp.ClientSession(timeout=timeout)

        for extension in EXTENSIONS:
            await self.load_extension(extension)
            LOGGER.info("Extensión cargada: %s", extension)

        if self.settings.sync_commands:
            if self.settings.dev_guild_id:
                guild = discord.Object(id=self.settings.dev_guild_id)
                self.tree.copy_global_to(guild=guild)
                synced = await self.tree.sync(guild=guild)
                LOGGER.info(
                    "%s comandos sincronizados en guild de desarrollo %s",
                    len(synced),
                    self.settings.dev_guild_id,
                )
            else:
                synced = await self.tree.sync()
                LOGGER.info("%s comandos globales sincronizados", len(synced))

    async def on_ready(self) -> None:
        if self.user is None:
            return

        await self.change_presence(
            activity=discord.CustomActivity(name=self.settings.default_status)
        )
        LOGGER.info(
            "PyBot conectado como %s (%s) en %s servidores",
            self.user,
            self.user.id,
            len(self.guilds),
        )

    async def close(self) -> None:
        if self.http_session is not None and not self.http_session.closed:
            await self.http_session.close()
        await self.database.close()
        await super().close()

    async def _on_app_command_error(
        self,
        interaction: discord.Interaction,
        error: app_commands.AppCommandError,
    ) -> None:
        original = getattr(error, "original", error)

        if isinstance(error, app_commands.CommandOnCooldown):
            message = f"Ese comando está en cooldown. Probá de nuevo en {error.retry_after:.1f}s."
        elif isinstance(error, app_commands.MissingPermissions):
            message = "No tenés los permisos necesarios para usar este comando."
        elif isinstance(error, app_commands.BotMissingPermissions):
            message = "Me faltan permisos de Discord para completar esa acción."
        elif isinstance(error, app_commands.CheckFailure):
            message = "No podés ejecutar ese comando en este contexto."
        else:
            LOGGER.exception(
                "Error no controlado en app command",
                exc_info=(type(original), original, original.__traceback__),
            )
            message = "Ocurrió un error inesperado. El incidente quedó registrado."

        if interaction.response.is_done():
            await interaction.followup.send(message, ephemeral=True)
        else:
            await interaction.response.send_message(message, ephemeral=True)
