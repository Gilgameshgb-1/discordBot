# bot.py
import os

import random
import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'{client.user.name} has connected to Discord!')

@client.event
async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send(
        f'Hi {member.name}, welcome to my Discord server!'
    )

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    tmp = [
        'https://www.klix.ba/biznis/finansije/hrvatska-namjerava-prodavati-narodne-obveznice-o-cemu-je-rijec-i-da-li-bih-treba-uraditi-isto/230205030'
    ]

    if message.content == 'test!':
        response = random.choice(tmp)
        await message.channel.send(response)

client.run(TOKEN)