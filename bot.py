import discord
from discord.ext import commands
import async

bot = commands.Bot("_")

@bot.event
async def on_ready():
    print("Bot Online")

@bot.command(pass_context=True)
async def ping(ctx):
    print(ctx)
    await bot.say("pong")

@bot.command(pass_context=True)
async def dank(ctx):
    await bot.say(":joy: :ok_hand:")

