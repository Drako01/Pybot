from __future__ import annotations

from datetime import UTC, datetime, timedelta

import discord
from discord import app_commands
from discord.ext import commands


class ModerationCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    async def _send_modlog(
        self,
        guild: discord.Guild,
        *,
        action: str,
        moderator: discord.abc.User,
        target: str,
        reason: str,
    ) -> None:
        settings = await self.bot.database.get_guild_settings(guild.id)  # type: ignore[attr-defined]
        if not settings.modlog_channel_id:
            return
        channel = guild.get_channel(settings.modlog_channel_id)
        if not isinstance(channel, discord.TextChannel):
            return

        embed = discord.Embed(
            title=f"🛡️ {action}",
            colour=discord.Colour.orange(),
            timestamp=datetime.now(UTC),
        )
        embed.add_field(name="Objetivo", value=target, inline=False)
        embed.add_field(name="Moderador", value=f"{moderator} (`{moderator.id}`)", inline=False)
        embed.add_field(name="Motivo", value=reason or "Sin motivo especificado", inline=False)
        await channel.send(embed=embed)

    @staticmethod
    def _can_moderate(interaction: discord.Interaction, member: discord.Member) -> tuple[bool, str]:
        guild = interaction.guild
        actor = interaction.user
        if guild is None or not isinstance(actor, discord.Member):
            return False, "Este comando sólo puede usarse dentro de un servidor."
        if member.id == actor.id:
            return False, "No podés moderarte a vos mismo."
        if member.id == guild.owner_id:
            return False, "No se puede moderar al owner del servidor."
        if actor.id != guild.owner_id and member.top_role >= actor.top_role:
            return False, "Ese miembro tiene un rol igual o superior al tuyo."
        if guild.me is not None and member.top_role >= guild.me.top_role:
            return False, "Mi rol debe estar por encima del miembro que querés moderar."
        return True, ""

    @app_commands.command(name="limpiar", description="Elimina una cantidad de mensajes recientes del canal.")
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(manage_messages=True)
    @app_commands.checks.bot_has_permissions(manage_messages=True, read_message_history=True)
    async def clear(self, interaction: discord.Interaction, cantidad: app_commands.Range[int, 1, 100]) -> None:
        channel = interaction.channel
        if not isinstance(channel, discord.TextChannel):
            await interaction.response.send_message("Este comando requiere un canal de texto.", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True, thinking=True)
        deleted = await channel.purge(limit=int(cantidad))
        await interaction.followup.send(f"✅ Se eliminaron **{len(deleted)}** mensajes.", ephemeral=True)

    @app_commands.command(name="timeout", description="Aísla temporalmente a un miembro.")
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(moderate_members=True)
    @app_commands.checks.bot_has_permissions(moderate_members=True)
    async def timeout(
        self,
        interaction: discord.Interaction,
        miembro: discord.Member,
        minutos: app_commands.Range[int, 1, 40320],
        motivo: str = "Sin motivo especificado",
    ) -> None:
        allowed, error = self._can_moderate(interaction, miembro)
        if not allowed:
            await interaction.response.send_message(f"❌ {error}", ephemeral=True)
            return

        until = datetime.now(UTC) + timedelta(minutes=int(minutos))
        await miembro.timeout(until, reason=f"{motivo} · por {interaction.user}")
        await interaction.response.send_message(
            f"✅ {miembro.mention} recibió timeout por **{minutos} min**.",
            ephemeral=True,
        )
        assert interaction.guild is not None
        await self._send_modlog(
            interaction.guild,
            action="Timeout",
            moderator=interaction.user,
            target=f"{miembro} (`{miembro.id}`)",
            reason=f"{motivo} · {minutos} min",
        )

    @app_commands.command(name="untimeout", description="Quita el timeout a un miembro.")
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(moderate_members=True)
    @app_commands.checks.bot_has_permissions(moderate_members=True)
    async def untimeout(
        self,
        interaction: discord.Interaction,
        miembro: discord.Member,
        motivo: str = "Timeout removido por moderación",
    ) -> None:
        allowed, error = self._can_moderate(interaction, miembro)
        if not allowed:
            await interaction.response.send_message(f"❌ {error}", ephemeral=True)
            return
        await miembro.timeout(None, reason=f"{motivo} · por {interaction.user}")
        await interaction.response.send_message(f"✅ Timeout removido a {miembro.mention}.", ephemeral=True)

    @app_commands.command(name="expulsar", description="Expulsa un miembro del servidor.")
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(kick_members=True)
    @app_commands.checks.bot_has_permissions(kick_members=True)
    async def kick(
        self,
        interaction: discord.Interaction,
        miembro: discord.Member,
        motivo: str = "Sin motivo especificado",
    ) -> None:
        allowed, error = self._can_moderate(interaction, miembro)
        if not allowed:
            await interaction.response.send_message(f"❌ {error}", ephemeral=True)
            return

        target = f"{miembro} (`{miembro.id}`)"
        await miembro.kick(reason=f"{motivo} · por {interaction.user}")
        await interaction.response.send_message(f"✅ **{miembro}** fue expulsado.", ephemeral=True)
        assert interaction.guild is not None
        await self._send_modlog(
            interaction.guild,
            action="Expulsión",
            moderator=interaction.user,
            target=target,
            reason=motivo,
        )

    @app_commands.command(name="banear", description="Banea un miembro del servidor.")
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(ban_members=True)
    @app_commands.checks.bot_has_permissions(ban_members=True)
    async def ban(
        self,
        interaction: discord.Interaction,
        miembro: discord.Member,
        motivo: str = "Sin motivo especificado",
        borrar_horas: app_commands.Range[int, 0, 168] = 0,
    ) -> None:
        allowed, error = self._can_moderate(interaction, miembro)
        if not allowed:
            await interaction.response.send_message(f"❌ {error}", ephemeral=True)
            return

        target = f"{miembro} (`{miembro.id}`)"
        await miembro.ban(
            reason=f"{motivo} · por {interaction.user}",
            delete_message_seconds=int(borrar_horas) * 3600,
        )
        await interaction.response.send_message(f"✅ **{miembro}** fue baneado.", ephemeral=True)
        assert interaction.guild is not None
        await self._send_modlog(
            interaction.guild,
            action="Ban",
            moderator=interaction.user,
            target=target,
            reason=motivo,
        )

    @app_commands.command(name="slowmode", description="Configura el slowmode del canal en segundos.")
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(manage_channels=True)
    @app_commands.checks.bot_has_permissions(manage_channels=True)
    async def slowmode(
        self,
        interaction: discord.Interaction,
        segundos: app_commands.Range[int, 0, 21600],
    ) -> None:
        channel = interaction.channel
        if not isinstance(channel, discord.TextChannel):
            await interaction.response.send_message("Este comando requiere un canal de texto.", ephemeral=True)
            return
        await channel.edit(slowmode_delay=int(segundos), reason=f"Configurado por {interaction.user}")
        text = "desactivado" if segundos == 0 else f"configurado en **{segundos}s**"
        await interaction.response.send_message(f"✅ Slowmode {text}.", ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(ModerationCog(bot))
