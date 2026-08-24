from __future__ import annotations

import logging
from datetime import UTC, datetime

import discord
from discord import app_commands
from discord.ext import commands, tasks

from pybot.utils.timeparse import parse_duration


LOGGER = logging.getLogger("pybot.reminders")


class RemindersCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.dispatch_due_reminders.start()

    def cog_unload(self) -> None:
        self.dispatch_due_reminders.cancel()

    @app_commands.command(name="recordar", description="Crea un recordatorio persistente.")
    async def remind(
        self,
        interaction: discord.Interaction,
        tiempo: str,
        mensaje: str,
    ) -> None:
        try:
            delta = parse_duration(tiempo)
        except ValueError as exc:
            await interaction.response.send_message(f"❌ {exc}", ephemeral=True)
            return

        if len(mensaje.strip()) < 2 or len(mensaje) > 500:
            await interaction.response.send_message(
                "El mensaje debe tener entre 2 y 500 caracteres.", ephemeral=True
            )
            return

        remind_at = datetime.now(UTC) + delta
        reminder_id = await self.bot.database.add_reminder(  # type: ignore[attr-defined]
            user_id=interaction.user.id,
            channel_id=interaction.channel_id,
            guild_id=interaction.guild_id,
            remind_at=remind_at,
            message=mensaje.strip(),
        )
        await interaction.response.send_message(
            f"⏰ Recordatorio **#{reminder_id}** creado para {discord.utils.format_dt(remind_at, style='R')}.",
            ephemeral=True,
        )

    @app_commands.command(name="recordatorios", description="Lista tus próximos recordatorios.")
    async def list_reminders(self, interaction: discord.Interaction) -> None:
        reminders = await self.bot.database.list_user_reminders(interaction.user.id)  # type: ignore[attr-defined]
        if not reminders:
            await interaction.response.send_message("No tenés recordatorios pendientes.", ephemeral=True)
            return

        lines = [
            f"**#{reminder.id}** · {discord.utils.format_dt(reminder.remind_at, style='R')} · {discord.utils.escape_markdown(reminder.message[:120])}"
            for reminder in reminders
        ]
        embed = discord.Embed(
            title="⏰ Tus recordatorios",
            description="\n".join(lines),
            colour=discord.Colour.blurple(),
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="borrar-recordatorio", description="Elimina uno de tus recordatorios.")
    async def delete_reminder(self, interaction: discord.Interaction, id: int) -> None:
        deleted = await self.bot.database.delete_reminder(id, interaction.user.id)  # type: ignore[attr-defined]
        message = "✅ Recordatorio eliminado." if deleted else "No encontré ese recordatorio entre los tuyos."
        await interaction.response.send_message(message, ephemeral=True)

    @tasks.loop(seconds=15)
    async def dispatch_due_reminders(self) -> None:
        reminders = await self.bot.database.get_due_reminders(datetime.now(UTC))  # type: ignore[attr-defined]
        for reminder in reminders:
            delivered = False
            channel = self.bot.get_channel(reminder.channel_id)
            if channel is None:
                try:
                    channel = await self.bot.fetch_channel(reminder.channel_id)
                except (discord.NotFound, discord.Forbidden, discord.HTTPException):
                    channel = None

            if isinstance(channel, (discord.TextChannel, discord.Thread, discord.DMChannel)):
                try:
                    await channel.send(
                        f"⏰ <@{reminder.user_id}> recordatorio: **{discord.utils.escape_markdown(reminder.message)}**",
                        allowed_mentions=discord.AllowedMentions(users=True),
                    )
                    delivered = True
                except discord.HTTPException:
                    LOGGER.exception("No se pudo entregar reminder %s", reminder.id)

            if delivered:
                await self.bot.database.delete_reminder(reminder.id)  # type: ignore[attr-defined]

    @dispatch_due_reminders.before_loop
    async def before_dispatch(self) -> None:
        await self.bot.wait_until_ready()


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(RemindersCog(bot))
