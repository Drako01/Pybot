from __future__ import annotations

import logging

import discord
from discord import app_commands
from discord.ext import commands


LOGGER = logging.getLogger("pybot.community")


class CommunityCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        settings = await self.bot.database.get_guild_settings(member.guild.id)  # type: ignore[attr-defined]

        if settings.autorole_id:
            role = member.guild.get_role(settings.autorole_id)
            if role is not None:
                try:
                    await member.add_roles(role, reason="Autorol configurado en PyBot")
                except discord.Forbidden:
                    LOGGER.warning("Sin permisos para asignar autorol en guild %s", member.guild.id)

        if settings.welcome_channel_id:
            channel = member.guild.get_channel(settings.welcome_channel_id)
            if isinstance(channel, discord.TextChannel):
                embed = discord.Embed(
                    title="👋 ¡Bienvenido/a!",
                    description=(
                        f"Hola {member.mention}, te damos la bienvenida a **{member.guild.name}**.\n"
                        f"Ya somos **{member.guild.member_count or 0}** miembros."
                    ),
                    colour=discord.Colour.green(),
                )
                embed.set_thumbnail(url=member.display_avatar.url)
                await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member) -> None:
        settings = await self.bot.database.get_guild_settings(member.guild.id)  # type: ignore[attr-defined]
        if not settings.farewell_channel_id:
            return

        channel = member.guild.get_channel(settings.farewell_channel_id)
        if isinstance(channel, discord.TextChannel):
            embed = discord.Embed(
                title="👋 Un miembro dejó el servidor",
                description=f"**{member.display_name}** dejó **{member.guild.name}**.",
                colour=discord.Colour.orange(),
            )
            embed.set_thumbnail(url=member.display_avatar.url)
            await channel.send(embed=embed)

    @app_commands.command(name="config-ver", description="Muestra la configuración de PyBot para este servidor.")
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(manage_guild=True)
    async def config_view(self, interaction: discord.Interaction) -> None:
        guild = interaction.guild
        assert guild is not None
        settings = await self.bot.database.get_guild_settings(guild.id)  # type: ignore[attr-defined]

        def channel_name(channel_id: int | None) -> str:
            if not channel_id:
                return "No configurado"
            channel = guild.get_channel(channel_id)
            return channel.mention if channel else f"ID `{channel_id}` (no encontrado)"

        def role_name(role_id: int | None) -> str:
            if not role_id:
                return "No configurado"
            role = guild.get_role(role_id)
            return role.mention if role else f"ID `{role_id}` (no encontrado)"

        embed = discord.Embed(
            title="⚙️ Configuración de PyBot",
            colour=discord.Colour.blurple(),
        )
        embed.add_field(name="Bienvenida", value=channel_name(settings.welcome_channel_id), inline=False)
        embed.add_field(name="Despedida", value=channel_name(settings.farewell_channel_id), inline=False)
        embed.add_field(name="Mod log", value=channel_name(settings.modlog_channel_id), inline=False)
        embed.add_field(name="Autorol", value=role_name(settings.autorole_id), inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="config-bienvenida", description="Configura o desactiva el canal de bienvenida.")
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(manage_guild=True)
    async def config_welcome(
        self,
        interaction: discord.Interaction,
        canal: discord.TextChannel | None = None,
    ) -> None:
        assert interaction.guild_id is not None
        await self.bot.database.update_guild_setting(  # type: ignore[attr-defined]
            interaction.guild_id, "welcome_channel_id", canal.id if canal else None
        )
        message = f"Canal de bienvenida: {canal.mention}." if canal else "Bienvenidas desactivadas."
        await interaction.response.send_message(f"✅ {message}", ephemeral=True)

    @app_commands.command(name="config-despedida", description="Configura o desactiva el canal de despedida.")
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(manage_guild=True)
    async def config_farewell(
        self,
        interaction: discord.Interaction,
        canal: discord.TextChannel | None = None,
    ) -> None:
        assert interaction.guild_id is not None
        await self.bot.database.update_guild_setting(  # type: ignore[attr-defined]
            interaction.guild_id, "farewell_channel_id", canal.id if canal else None
        )
        message = f"Canal de despedida: {canal.mention}." if canal else "Despedidas desactivadas."
        await interaction.response.send_message(f"✅ {message}", ephemeral=True)

    @app_commands.command(name="config-modlog", description="Configura o desactiva el canal de auditoría de moderación.")
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(manage_guild=True)
    async def config_modlog(
        self,
        interaction: discord.Interaction,
        canal: discord.TextChannel | None = None,
    ) -> None:
        assert interaction.guild_id is not None
        await self.bot.database.update_guild_setting(  # type: ignore[attr-defined]
            interaction.guild_id, "modlog_channel_id", canal.id if canal else None
        )
        message = f"Canal de mod log: {canal.mention}." if canal else "Mod log desactivado."
        await interaction.response.send_message(f"✅ {message}", ephemeral=True)

    @app_commands.command(name="config-autorol", description="Configura o desactiva el rol automático para nuevos miembros.")
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(manage_roles=True)
    async def config_autorole(
        self,
        interaction: discord.Interaction,
        rol: discord.Role | None = None,
    ) -> None:
        assert interaction.guild_id is not None
        guild = interaction.guild
        assert guild is not None

        if rol is not None and guild.me is not None and rol >= guild.me.top_role:
            await interaction.response.send_message(
                "❌ Ese rol está por encima (o al mismo nivel) que mi rol más alto.",
                ephemeral=True,
            )
            return

        await self.bot.database.update_guild_setting(  # type: ignore[attr-defined]
            interaction.guild_id, "autorole_id", rol.id if rol else None
        )
        message = f"Autorol configurado: {rol.mention}." if rol else "Autorol desactivado."
        await interaction.response.send_message(f"✅ {message}", ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(CommunityCog(bot))
