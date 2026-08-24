from __future__ import annotations

from datetime import UTC, datetime

import discord
from discord import app_commands
from discord.ext import commands

from pybot import __version__


class CoreCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="ayuda", description="Muestra los módulos y comandos principales de PyBot.")
    async def help_command(self, interaction: discord.Interaction) -> None:
        embed = discord.Embed(
            title="🐍 PyBot · Centro de ayuda",
            description=(
                "Bot comunitario construido con Python y discord.py. "
                "Los comandos están organizados por función y usan slash commands."
            ),
            colour=discord.Colour.blurple(),
            timestamp=datetime.now(UTC),
        )
        embed.add_field(
            name="🧭 General",
            value="`/ping` `/about` `/serverinfo` `/userinfo` `/avatar`",
            inline=False,
        )
        embed.add_field(
            name="🛠️ Utilidades",
            value="`/dolar` `/encuesta` `/elegir` `/dado` `/moneda` `/mapa`",
            inline=False,
        )
        embed.add_field(
            name="⏰ Recordatorios",
            value="`/recordar` `/recordatorios` `/borrar-recordatorio`",
            inline=False,
        )
        embed.add_field(
            name="🎭 Comunidad",
            value="`/roles` `/rol` · administración con `/config-*`",
            inline=False,
        )
        embed.add_field(
            name="🛡️ Moderación",
            value="`/limpiar` `/timeout` `/untimeout` `/expulsar` `/banear` `/slowmode`",
            inline=False,
        )
        embed.set_footer(text=f"PyBot v{__version__} · consultá README/docs para referencia completa")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="ping", description="Mide la latencia actual del bot.")
    async def ping(self, interaction: discord.Interaction) -> None:
        latency_ms = round(self.bot.latency * 1000)
        await interaction.response.send_message(
            f"🏓 Pong · **{latency_ms} ms**",
            ephemeral=True,
        )

    @app_commands.command(name="about", description="Información técnica y versión de PyBot.")
    async def about(self, interaction: discord.Interaction) -> None:
        embed = discord.Embed(
            title="🐍 PyBot",
            description="Bot modular para comunidades de Discord, desarrollado en Python.",
            colour=discord.Colour.blurple(),
        )
        embed.add_field(name="Versión", value=__version__)
        embed.add_field(name="Framework", value=f"discord.py {discord.__version__}")
        embed.add_field(name="Servidores", value=str(len(self.bot.guilds)))
        embed.add_field(
            name="Autor",
            value="[Alejandro Daniel Di Stefano](https://github.com/Drako01)",
            inline=False,
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="serverinfo", description="Muestra información del servidor actual.")
    @app_commands.guild_only()
    async def server_info(self, interaction: discord.Interaction) -> None:
        guild = interaction.guild
        assert guild is not None
        owner = guild.owner.mention if guild.owner else "No disponible"
        embed = discord.Embed(
            title=f"📊 {guild.name}",
            colour=discord.Colour.blurple(),
            timestamp=datetime.now(UTC),
        )
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        embed.add_field(name="Miembros", value=str(guild.member_count or 0))
        embed.add_field(name="Canales", value=str(len(guild.channels)))
        embed.add_field(name="Roles", value=str(len(guild.roles)))
        embed.add_field(name="Owner", value=owner, inline=False)
        embed.add_field(
            name="Creado",
            value=discord.utils.format_dt(guild.created_at, style="D"),
            inline=False,
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="userinfo", description="Muestra información de un miembro.")
    @app_commands.guild_only()
    async def user_info(
        self,
        interaction: discord.Interaction,
        miembro: discord.Member | None = None,
    ) -> None:
        member = miembro or interaction.user
        if not isinstance(member, discord.Member):
            await interaction.response.send_message("No pude resolver ese miembro.", ephemeral=True)
            return

        embed = discord.Embed(
            title=f"👤 {member.display_name}",
            colour=member.colour if member.colour.value else discord.Colour.blurple(),
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="Usuario", value=str(member))
        embed.add_field(name="ID", value=str(member.id))
        embed.add_field(
            name="Cuenta creada",
            value=discord.utils.format_dt(member.created_at, style="R"),
            inline=False,
        )
        if member.joined_at:
            embed.add_field(
                name="Ingresó al servidor",
                value=discord.utils.format_dt(member.joined_at, style="R"),
                inline=False,
            )
        embed.add_field(name="Roles", value=str(max(0, len(member.roles) - 1)))
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="avatar", description="Muestra el avatar de un usuario en alta resolución.")
    async def avatar(
        self,
        interaction: discord.Interaction,
        usuario: discord.User | None = None,
    ) -> None:
        target = usuario or interaction.user
        embed = discord.Embed(
            title=f"Avatar de {target.display_name}",
            colour=discord.Colour.blurple(),
        )
        embed.set_image(url=target.display_avatar.url)
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(CoreCog(bot))
