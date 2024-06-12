# bot.py
import discord
from discord.ext import commands
from discord import *
from dotenv import load_dotenv
import os
import events 

print("Iniciando Bot...\n")

# Carga las variables de entorno desde el archivo .env
load_dotenv()
TOKEN = os.getenv('DISCORD_KEY')
WELCOME_CHANNEL_ID = os.getenv('WELCOME_CHANNEL_ID')


# Crea una instancia de la clase Bot con los intentos especificados
intents = discord.Intents.default()
intents.members = True  
intents.message_content = True


bot = commands.Bot(command_prefix='!', intents=intents)

# Crear un diccionario para mantener un registro de las salas de voz en las que el bot se encuentra
voice_channels = {}

# Registra los eventos utilizando el decorador @bot.event
@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user}')

@bot.event
async def on_member_join(member):
    await events.on_member_join(member, bot)

@bot.event
async def on_member_join(member):
    # Obtén el canal de bienvenida usando el método bot.get_channel
    welcome_channel = bot.get_channel(WELCOME_CHANNEL_ID)
    if welcome_channel:
        await welcome_channel.send(f'¡Bienvenido al servidor {member.mention}! Actualmente hay {member.guild.member_count} miembros.')
    await events.on_member_join(member, bot)
    
@bot.event
async def on_member_remove(member):
    await events.on_member_remove(member, bot)

@bot.event
async def on_message(message):
    await events.on_message(message, bot)

@bot.event
async def on_raw_reaction_add(payload):
    await events.on_raw_reaction_add(payload, bot)
    
bot.run(TOKEN)
