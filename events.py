# events-py
import discord
import urllib.parse
import requests
import os
from dotenv import load_dotenv


load_dotenv()
url = os.getenv('API_DOLAR')
google = os.getenv('API_GOOGLE')

async def on_raw_reaction_add(payload, bot):
    if payload.member.bot:
        return

    channel = bot.get_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
    guild = message.guild

    member = payload.member

    try:
        emoji = payload.emoji.name
        role = discord.utils.get(guild.roles, name=emoji)
        
        if role is not None:
            if role in member.roles:
                await member.remove_roles(role)
            else:
                await member.add_roles(role)

    except Exception as e:
        print(f'Error: {e}')
        
# Evento que se ejecuta cuando un nuevo miembro se une al servidor
async def on_member_join(member, bot):
    guild = member.guild
    canal_de_bienvenida = discord.utils.get(guild.channels, name="bienvenida")

    if canal_de_bienvenida:
        mensaje_de_bienvenida = f'Bienvenido al servidor, {member.mention}!'
        await canal_de_bienvenida.send(mensaje_de_bienvenida)
    
    channel = bot.get_channel(1242557348229419149) 
    message = await channel.send(f'Bienvenido {member.mention}! Reacciona a este mensaje para seleccionar tus roles:')

    for emoji in ['👨‍💻', '📂', '⌨️', '💻', '🖥️', '🎨', '👁️']:
        await message.add_reaction(emoji)

async def obtener_usuarios_offline(message):
    usuarios_offline = [m for m in message.guild.members if m.status == discord.Status.offline]

    if usuarios_offline:
        lista_usuarios = "\n".join([u.display_name for u in usuarios_offline])
        respuesta = f'Los usuarios que están offline son:\n{lista_usuarios}'
    else:
        respuesta = 'No hay usuarios offline en este servidor en este momento.'

    await message.channel.send(respuesta)

# Evento que se ejecuta cuando se recibe un mensaje en el servidor
async def on_message(message, bot):
    if message.author == bot.user:
        return

    mensaje = message.content.lower()

    if ("dolar" in mensaje or "dólar" in mensaje or "euro" in mensaje) and (("oficial" in mensaje or "blue" in mensaje) and ("compra" in mensaje or "venta" in mensaje)):
        tipo = "oficial" if "oficial" in mensaje else "blue" if "blue" in mensaje else "oficial_euro" if "euro" in mensaje else "blue_euro"
        accion = "compra" if "compra" in mensaje else "venta"

        # Obtener el valor del dólar o euro
        
        response = requests.get(url)

        if response.status_code == 200:
            data_dolar = response.json()
            clave_valor = "value_buy" if accion == "compra" else "value_sell"
            valor = data_dolar[tipo][clave_valor]

            if "euro" in mensaje:
                moneda = "Euro"
            else:
                moneda = "Dólar"

            mensaje_respuesta = f"El Valor del {moneda} {tipo.replace('_', ' ').title()} es de ${valor} para la {accion.title()}"
            await message.channel.send(mensaje_respuesta)
        else:
            await message.channel.send("No se pudo obtener la información de la moneda en este momento. Inténtalo de nuevo más tarde.")

    if mensaje.startswith('¿dónde queda '):
        provincia = mensaje[len('¿dónde queda '):-1]
        ubicacion_codificada = urllib.parse.quote(provincia)        
        google_maps_url = f'{google}{ubicacion_codificada}'

        await message.channel.send(f'{provincia} se encuentra en {google_maps_url}')

    if bot.user.mentioned_in(message):
        apodo = message.author.mention
        if any(saludo in mensaje for saludo in ["hola", "hello", "hi", "Buen dia", "Buenas tardes", "Buenas noches"]):
            respuesta = f'Hola {apodo}! ¿Cómo estas en el día de hoy?'
        elif any(saludo in mensaje for saludo in ["adios", "chau", "bye"]):
            respuesta = f'Hasta luego {apodo}!'
        elif any(saludo in mensaje for saludo in ["ayudar", "ayuda", "help", "ayudame"]):
            respuesta = f'Obviamente, ¿en qué te puedo ayudar {apodo}?'
        elif any(saludo in mensaje for saludo in ["sos", "robot", "extraterreste"]):
            respuesta = f'Para nada {apodo}, soy un Bot generado con Python por un Hacker!.'
        elif "offline" in mensaje:
            await obtener_usuarios_offline(message)
            return
        else:
            respuesta = f'Quedo atento a lo que necesites {apodo}!'
    
        await message.channel.send(respuesta)
