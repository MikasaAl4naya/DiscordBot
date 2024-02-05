import asyncio
import os
import discord
from commands import Commands
from dotenv import load_dotenv
from DisBot import bot, load_available_words
load_dotenv()

coms = Commands(bot)

@bot.event
async def on_ready():
    print(f'{bot.user} has logged in.')
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            # cut off the .py from the file name
            await bot.load_extension(f"cogs.{filename[:-3]}")
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.listening, name='Шамана'))
    await load_available_words()
    print(f'{bot.user} has')

TOKEN = os.getenv('DISCORD_BOT_TOKEN')

bot.run(TOKEN)
