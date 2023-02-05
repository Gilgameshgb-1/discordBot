import os
import random
import discord

from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.command(name='test', help = 'Respons with a random line from the Backstreets boy "I want it that way."')
async def nine_nine(ctx):
    test = ['aint nothing but a heartache',
                'aint nothing but a mistake',
                'i dont ever wanna hear you say',
                'i want it that way']

    response = random.choice(test)
    await ctx.send(response)

@bot.command(name='rollDice', help='Simulates rolling dice.')
async def roll(ctx, number_of_dice: int, number_of_sides: int):
    dice = [
        str(random.choice(range(1, number_of_sides + 1)))
        for _ in range(number_of_dice)
    ]
    await ctx.send('The dice rolls are: ')
    await ctx.send(', '.join(dice))
    await ctx.send('Ako citas ovo, volim te. <3')

@bot.command(name='createChannel')
@commands.has_role('admin')
async def create_channel(ctx, channel_name):
    guild = ctx.guild
    existing_channel = discord.utils.get(guild.channels, name=channel_name)
    if not existing_channel:
        print(f'Creating a new channel: {channel_name}')
        await guild.create_text_channel(channel_name)

bot.run(TOKEN)