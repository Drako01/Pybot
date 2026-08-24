from __future__ import annotations

import random
import urllib.parse
from datetime import UTC, datetime

import discord
from discord import app_commands
from discord.ext import commands


DOLLAR_CHOICES = [
    app_commands.Choice(name="Oficial", value="oficial"),
    app_commands.Choice(name="Blue", value="blue"),
    app_commands.Choice(name="MEP / Bolsa", value="bolsa"),
    app_commands.Choice(name="CCL", value="contadoconliqui"),
    app_commands.Choice(name="Tarjeta", value="tarjeta"),
    app_commands.Choice(name="Mayorista", value="mayorista"),
    app_commands.Choice(name="Cripto", value="cripto"),
]


class UtilitiesCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="dolar", description="Consulta una cotización actual del dólar en Argentina.")
    @app_commands.choices(tipo=DOLLAR_CHOICES)
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: i.user.id)
    async def dollar(
        self,
        interaction: discord.Interaction,
        tipo: app_commands.Choice[str],
    ) -> None:
        await interaction.response.defer(thinking=True)
        session = self.bot.http_session  # type: ignore[attr-defined]
        if session is None:
            await interaction.followup.send("El cliente HTTP todavía no está disponible.", ephemeral=True)
            return

        base_url = self.bot.settings.currency_api_base_url  # type: ignore[attr-defined]
        url = f"{base_url}/dolares/{tipo.value}"
        try:
            async with session.get(url) as response:
                if response.status != 200:
                    raise RuntimeError(f"HTTP {response.status}")
                data = await response.json()
        except Exception:
            await interaction.followup.send(
                "No pude obtener la cotización en este momento. Probá nuevamente más tarde.",
                ephemeral=True,
            )
            return

        embed = discord.Embed(
            title=f"💵 {data.get('nombre', tipo.name)}",
            colour=discord.Colour.green(),
            timestamp=datetime.now(UTC),
        )
        embed.add_field(name="Compra", value=f"$ {data.get('compra', 'N/D')}")
        embed.add_field(name="Venta", value=f"$ {data.get('venta', 'N/D')}")
        updated = data.get("fechaActualizacion")
        if updated:
            embed.add_field(name="Actualización", value=str(updated), inline=False)
        embed.set_footer(text="Fuente: DolarAPI.com")
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="encuesta", description="Crea una encuesta rápida con hasta cinco opciones.")
    @app_commands.guild_only()
    async def poll(
        self,
        interaction: discord.Interaction,
        pregunta: str,
        opcion_1: str,
        opcion_2: str,
        opcion_3: str | None = None,
        opcion_4: str | None = None,
        opcion_5: str | None = None,
    ) -> None:
        options = [option for option in [opcion_1, opcion_2, opcion_3, opcion_4, opcion_5] if option]
        emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"]
        description = "\n".join(f"{emojis[index]} {option}" for index, option in enumerate(options))
        embed = discord.Embed(
            title=f"📊 {pregunta[:240]}",
            description=description,
            colour=discord.Colour.blurple(),
        )
        embed.set_footer(text=f"Encuesta creada por {interaction.user.display_name}")
        await interaction.response.send_message(embed=embed)
        message = await interaction.original_response()
        for emoji in emojis[: len(options)]:
            await message.add_reaction(emoji)

    @app_commands.command(name="elegir", description="Elige aleatoriamente entre opciones separadas por |.")
    async def choose(self, interaction: discord.Interaction, opciones: str) -> None:
        values = [item.strip() for item in opciones.split("|") if item.strip()]
        if len(values) < 2:
            await interaction.response.send_message(
                "Ingresá al menos dos opciones separadas por `|`. Ejemplo: `pizza | sushi | empanadas`.",
                ephemeral=True,
            )
            return
        await interaction.response.send_message(f"🎯 Elijo: **{random.choice(values)}**")

    @app_commands.command(name="dado", description="Tira uno o más dados.")
    async def dice(
        self,
        interaction: discord.Interaction,
        caras: app_commands.Range[int, 2, 1000] = 6,
        cantidad: app_commands.Range[int, 1, 10] = 1,
    ) -> None:
        rolls = [random.randint(1, int(caras)) for _ in range(int(cantidad))]
        await interaction.response.send_message(
            f"🎲 Resultado: **{', '.join(map(str, rolls))}** · total **{sum(rolls)}**"
        )

    @app_commands.command(name="moneda", description="Lanza una moneda virtual.")
    async def coin(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message(f"🪙 **{random.choice(['Cara', 'Cruz'])}**")

    @app_commands.command(name="mapa", description="Genera un enlace de búsqueda en Google Maps.")
    async def map_link(self, interaction: discord.Interaction, lugar: str) -> None:
        encoded = urllib.parse.quote_plus(lugar.strip())
        url = f"https://www.google.com/maps/search/?api=1&query={encoded}"
        embed = discord.Embed(
            title="🗺️ Buscar ubicación",
            description=f"[{discord.utils.escape_markdown(lugar)}]({url})",
            colour=discord.Colour.blurple(),
        )
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(UtilitiesCog(bot))
