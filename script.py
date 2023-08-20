import os
import random
import discord
import json

from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    global gas_points
    print(f'Logged in as {bot.user.name}')
    
    # Load data from file
    gas_points = load_from_file('gas.json')
    print('Gas points data loaded:', gas_points)

def save_to_file(data, filename):
    with open(filename, 'w') as file:
        json.dump(data, file)

def load_from_file(filename):
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

@bot.command()
async def dodajGasPoene(ctx, user: discord.Member, amount: int):
    if(amount < 0):
        await ctx.send(f"Sta ti je DEBILU")
        return
    elif(amount == 0):
        await ctx.send(f"BRAVO MAJSTORE 0 bodova si dodao")
        return
    if any(role.name == "dodavacGasa" for role in ctx.author.roles):
        if str(user.id) in gas_points:
            gas_points[str(user.id)] += amount
        else:
            gas_points[str(user.id)] = amount
        
        save_to_file(gas_points, 'gas.json')
        await ctx.send(f"{amount} Dodan gas poen {user.name}. Ukupni gas: {gas_points[str(user.id)]}")
    else:
        await ctx.send("Ne mozes ti dodavat DEBILU.")

@bot.command()
async def skiniGasPoene(ctx, user: discord.Member, amount: int):
    if(amount < 0):
        await ctx.send(f"Sta ti je DEBILU")
        return
    elif(amount == 0):
        await ctx.send(f"BRAVO MAJSTORE 0 bodova si oduzeo")
        return
    if any(role.name == "dodavacGasa" for role in ctx.author.roles):
        #print(type(user.id))
        #print(gas_points[str(user.id)])
        if str(user.id) in gas_points:
            gas_points[str(user.id)] -= amount
        else:
            gas_points[str(user.id)] = amount
        
        save_to_file(gas_points, 'gas.json')
        await ctx.send(f"{amount} Skinut gas poen {user.name}. Ukupni gas: {gas_points[str(user.id)]}")
    else:
        await ctx.send("Ne mozes ti oduzimat DEBILU.")

@bot.command()
async def dajStanjeGasa(ctx):
    report = "Gas leaderboard:\n\n"

    sorted_gas_points = dict(sorted(gas_points.items(), key=lambda item: item[1], reverse=True))
    index = 0

    for user_id, points in sorted_gas_points.items():
        index += 1
        member = ctx.guild.get_member(int(user_id))
        if member:
            display_name = member.display_name.capitalize()
            if index == 1:
                display_name = "🥇 " + display_name
            elif index == 2:
                display_name = "🥈 " + display_name
            elif index == 3:
                display_name = "🥉 " + display_name
            report += f"{index}. {display_name}: {points} points\n"
        else:
            report += f"User ID {user_id}: {points} points (User not found in server)\n"
    
    await ctx.send(report)
    

@bot.command(name='createChannel')
@commands.has_role('admin')
async def create_channel(ctx, channel_name):
    guild = ctx.guild
    existing_channel = discord.utils.get(guild.channels, name=channel_name)
    if not existing_channel:
        print(f'Creating a new channel: {channel_name}')
        await guild.create_text_channel(channel_name)

bot.run(TOKEN)