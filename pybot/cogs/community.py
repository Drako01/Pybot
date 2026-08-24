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

    @app_commands.command(name="roles", description="Muestra los roles que los miembros pueden autoasignarse.")
    @app_commands.guild_only()
    async def self_roles(self, interaction: discord.Interaction) -> None:
        guild = interaction.guild
        assert guild is not None
        role_ids = await self.bot.database.list_self_roles(guild.id)  # type: ignore[attr-defined]
        roles = [guild.get_role(role_id) for role_id in role_ids]
        valid_roles = [role for role in roles if role is not None]

        if not valid_roles:
            await interaction.response.send_message(
                "Este servidor todavía no configuró roles autoasignables.", ephemeral=True
            )
            return

        embed = discord.Embed(
            title="🎭 Roles autoasignables",
            description="\n".join(f"• {role.mention}" for role in valid_roles),
            colour=discord.Colour.blurple(),
        )
        embed.set_footer(text="Usá /rol para agregar o quitar uno de estos roles")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="rol", description="Agrega o quita un rol autoasignable de tu perfil.")
    @app_commands.guild_only()
    @app_commands.checks.bot_has_permissions(manage_roles=True)
    async def self_role(self, interaction: discord.Interaction, rol: discord.Role) -> None:
        guild = interaction.guild
        member = interaction.user
        assert guild is not None
        if not isinstance(member, discord.Member):
            await interaction.response.send_message("No pude resolver tu membresía.", ephemeral=True)
            return

        allowed_ids = await self.bot.database.list_self_roles(guild.id)  # type: ignore[attr-defined]
        if rol.id not in allowed_ids:
            await interaction.response.send_message(
                "❌ Ese rol no está habilitado para autoasignación. Usá `/roles` para ver los disponibles.",
                ephemeral=True,
            )
            return

        if guild.me is None or rol >= guild.me.top_role or rol.managed:
            await interaction.response.send_message(
                "❌ No puedo administrar ese rol por la jerarquía o porque es un rol gestionado.",
                ephemeral=True,
            )
            return

        if rol in member.roles:
            await member.remove_roles(rol, reason="Autoasignación mediante PyBot")
            message = f"➖ Se quitó {rol.mention}."
        else:
            await member.add_roles(rol, reason="Autoasignación mediante PyBot")
            message = f"✅ Se agregó {rol.mention}."
        await interaction.response.send_message(message, ephemeral=True)

    @app_commands.command(name="config-ver", description="Muestra la configuración de PyBot para este servidor.")
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(manage_guild=True)
    async def config_view(self, interaction: discord.Interaction) -> None:
        guild = interaction.guild
        assert guild is not None
        settings = await self.bot.database.get_guild_settings(guild.id)  # type: ignore[attr-defined]
        self_role_ids = await self.bot.database.list_self_roles(guild.id)  # type: ignore[attr-defined]

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

        self_roles = [guild.get_role(role_id) for role_id in self_role_ids]
        self_role_text = ", ".join(role.mention for role in self_roles if role is not None) or "Ninguno"

        embed = discord.Embed(
            title="⚙️ Configuración de PyBot",
            colour=discord.Colour.blurple(),
        )
        embed.add_field(name="Bienvenida", value=channel_name(settings.welcome_channel_id), inline=False)
        embed.add_field(name="Despedida", value=channel_name(settings.farewell_channel_id), inline=False)
        embed.add_field(name="Mod log", value=channel_name(settings.modlog_channel_id), inline=False)
        embed.add_field(name="Autorol", value=role_name(settings.autorole_id), inline=False)
        embed.add_field(name="Roles autoasignables", value=self_role_text, inline=False)
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

        if rol is not None and (rol.managed or (guild.me is not None and rol >= guild.me.top_role)):
            await interaction.response.send_message(
                "❌ Ese rol no puede ser administrado por el bot o está por encima de mi rol más alto.",
                ephemeral=True,
            )
            return

        await self.bot.database.update_guild_setting(  # type: ignore[attr-defined]
            interaction.guild_id, "autorole_id", rol.id if rol else None
        )
        message = f"Autorol configurado: {rol.mention}." if rol else "Autorol desactivado."
        await interaction.response.send_message(f"✅ {message}", ephemeral=True)

    @app_commands.command(name="config-rol-agregar", description="Habilita un rol para autoasignación por los miembros.")
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(manage_roles=True)
    async def config_self_role_add(self, interaction: discord.Interaction, rol: discord.Role) -> None:
        guild = interaction.guild
        assert guild is not None
        if rol.is_default() or rol.managed or (guild.me is not None and rol >= guild.me.top_role):
            await interaction.response.send_message(
                "❌ Ese rol no es apto para autoasignación o está fuera de mi jerarquía.", ephemeral=True
            )
            return
        await self.bot.database.add_self_role(guild.id, rol.id)  # type: ignore[attr-defined]
        await interaction.response.send_message(
            f"✅ {rol.mention} quedó habilitado para `/rol`.", ephemeral=True
        )

    @app_commands.command(name="config-rol-quitar", description="Quita un rol de la lista de autoasignables.")
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(manage_roles=True)
    async def config_self_role_remove(self, interaction: discord.Interaction, rol: discord.Role) -> None:
        guild = interaction.guild
        assert guild is not None
        removed = await self.bot.database.remove_self_role(guild.id, rol.id)  # type: ignore[attr-defined]
        message = f"✅ {rol.mention} ya no es autoasignable." if removed else "Ese rol no estaba configurado."
        await interaction.response.send_message(message, ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(CommunityCog(bot))
