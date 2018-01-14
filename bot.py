import discord
from discord.ext import commands
import async
import random
from .fortunas import fortunas
import bot.scraper as scraper

bot = commands.Bot(command_prefix="_")

@bot.event
async def on_ready():
    print("Bot Online")

@bot.event
async def on_message(message):
    if message.content.startswith("_chan"):
        await bot.send_message(message.channel,scraper.main_screen())
        def check(m):
            pass
        #msg = await bot.wait_for_message(author=message.author,timeout=10)#,check=check)
        return

    elif message.content.startswith("_ping"):
        await bot.send_message(message.channel,":ping_pong: pong")
    
    elif message.content.startswith("_fortuna"):
        await bot.send_message(message.channel,fortunas[random.randint(0,len(fortunas)-1)])
    
    else:
        return

#Luis Albizo 13/01/18
