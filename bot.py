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
        msg = await bot.wait_for_message(author=message.author,timeout=10)
        if not(msg):
            return
        response = scraper.goto_board(msg.content.strip())
        if response["error"]:
            await bot.send_message(message.channel,response["content"])
            return
        else:
            await bot.send_message(message.channel,response["content"][0])
            for el in response["content"][1]:
                await bot.send_message(message.channel,el)
            await bot.send_message(message.channel,response["content"][2])
            msg = await bot.wait_for_message(author=message.author,timeout=10)
            #try:
            ids=int(msg.content)
            for img in scraper.get_thread_files(response["threads"][ids]["post_url"]):
                await bot.send_message(message.channel,img)
            return
            #except:
                #return

    elif message.content.startswith("_ping"):
        await bot.send_message(message.channel,":ping_pong: pong")
    
    elif message.content.startswith("_fortuna"):
        await bot.send_message(message.channel,fortunas[random.randint(0,len(fortunas)-1)])
    
    else:
        return

#Luis Albizo 13/01/18
