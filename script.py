import os
import random
import discord
import json
import asyncio

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

@bot.command(help="Komanda za skidanje gas poena")
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
            report += f"{index}. {display_name}: {points} poena\n"
        else:
            report += f"User ID {user_id}: {points} points (User not found in server)\n"
    
    await ctx.send(report)
    
@bot.command()
async def daVidimGas(ctx, user: discord.Member):
    member = ctx.guild.get_member(int(user.id))
    if(member):
        await ctx.send(f"{ctx.guild.get_member(int(user.id)).display_name.capitalize()} Gas: {gas_points[str(user.id)]}")
    else:
        await ctx.send(f"Taj ti ne postoji brt")

deduct_words = ["dislajt", "termin", "nba", "honkai", "hsr"] 

@bot.event
async def on_message(message):
    if not message.author.bot:
        for deduct_word in deduct_words:
            if deduct_word in message.content.lower():
                user_id = str(message.author.id)
                if user_id in gas_points:
                    gas_points[user_id] -= 1  
                    save_to_file(gas_points, 'gas.json')
                    await message.channel.send(f"Gas poen skinut {message.author.mention}-u. Trenutni Gas: {gas_points[user_id]}")
                    break  
                
    await bot.process_commands(message) 

@bot.command()
async def zabranjeneRijeci(ctx):
    deductions = "\n".join(deduct_words)
    await ctx.send(f"Za ovo se skida gas: {deductions}")

@bot.command()
async def glasanjeZaGas(ctx, user: discord.Member, amount: int):
    vote_message = f"Da li cemo mu dati gas?\n\n"
    vote_message += "👍 Yes\n\n"
    vote_message += "👎 No\n"

    vote_embed = discord.Embed(description=vote_message, color=0x00ff00)
    vote_embed.set_footer(text="Reagujte sa 👍 ili 👎 da biste glasali!")

    vote_msg = await ctx.send(embed=vote_embed)
    await vote_msg.add_reaction("👍")
    await vote_msg.add_reaction("👎")

    await asyncio.sleep(5) 

    thumbs_up_count = 0
    thumbs_down_count = 0

    message = await ctx.fetch_message(vote_msg.id)
    for reaction in message.reactions:
        if reaction.emoji == "👍":
            thumbs_up_count = reaction.count - 1
        elif reaction.emoji == "👎":
            thumbs_down_count = reaction.count - 1

    if thumbs_up_count > thumbs_down_count:
        await ctx.send("Dodan gas!")
        gas_points[str(user.id)] += amount
        save_to_file(gas_points, 'gas.json')
    elif thumbs_down_count > thumbs_up_count:
        await ctx.send("Nema gasa!")
    else:
        await ctx.send("Ne mozete da se DOGOVORITE!")


@bot.event
async def on_reaction_add(reaction, user):
    if user != bot.user:
        message = reaction.message
        if message.author == bot.user and message.embeds:
            embed = message.embeds[0]
            if "Reagujte sa 👍 ili 👎 da biste glasali!" in embed.footer.text:
                if reaction.emoji in ["👍", "👎"]:
                    # Register the vote
                    vote_option = "Da" if reaction.emoji == "👍" else "Ne"
                    print(f"User {user} voted: {vote_option}")

@bot.command(name='createChannel')
@commands.has_role('admin')
async def create_channel(ctx, channel_name):
    guild = ctx.guild
    existing_channel = discord.utils.get(guild.channels, name=channel_name)
    if not existing_channel:
        print(f'Creating a new channel: {channel_name}')
        await guild.create_text_channel(channel_name)

bot.run(TOKEN)