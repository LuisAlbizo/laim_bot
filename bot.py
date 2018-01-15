import discord
from discord.ext import commands
import async
import random
from .fortunas import fortunas
import bot.scraper as scraper
import time

bot = commands.Bot(command_prefix="_")
#discord.member.utils.find(lambda m: m.id = "401391614838439936",channel.server.members)

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

@bot.command(pass_context=True)
async def fortuna(ctx):
    await bot.say(fortunas[random.randint(0,len(fortunas)-1)])

@bot.event
async def on_message(message):
    if message.content.startswith("_chan"):
        fm = await bot.send_message(message.channel,scraper.main_screen())
        msg = await bot.wait_for_message(author=message.author,timeout=15)
        if not(msg):
            return
        await bot.delete_message(fm)
        response = scraper.goto_board(msg.content.strip())
        if response["error"]:
            fm = await bot.send_message(message.channel,response["content"])
            time.sleep(5)
            await bot.delete_message(fm)
            return
        else:
            fm = await bot.send_message(message.channel,response["content"][0])
            i=1
            hilos = list(response["content"][1])
            while True:
                el = hilos[i-1]
                page = await bot.send_message(message.channel,el)
                if i>1:
                    await bot.add_reaction(page,"\u25C0")#anterior
                if i<15:
                    await bot.add_reaction(page,"\u25B6")#siguiente
                await bot.add_reaction(page,"\u2611")#seleccionar
                await bot.add_reaction(page,"\u274E")#quitar
                opc = await bot.wait_for_reaction(
                        ["\u25C0","\u25B6","\u2611","\u274E"],user=message.author,message=page,timeout=15)
                print(opc)
                if not(opc):
                    await bot.delete_message(fm)
                    await bot.delete_message(page)
                    return
                else:
                    await bot.delete_message(page)
                    if opc.reaction.emoji=="\u25C0":
                        i-=1
                        pass
                    elif opc.reaction.emoji=="\u25B6":
                        i+=1
                        pass
                    elif opc.reaction.emoji=="\u2611":
                        break
                    elif opc.reaction.emoji=="\u274E":
                        return
            await bot.delete_message(fm)
            ids=i
            i=0
            imgs = list(scraper.get_thread_files(response["threads"][ids]["post_url"]))
            page = await bot.send_message(message.channel,"loading...")
            while True:
                img = imgs[i]
                await bot.edit_message(page,(("image %i of %i\n" % (i+1,len(imgs)))+img))
                if i>0:
                    await bot.add_reaction(page,"\u25C0")#anterior
                if i<len(imgs)-1:
                    await bot.add_reaction(page,"\u25B6")#siguiente
                await bot.add_reaction(page,"\u2611")#seleccionar
                await bot.add_reaction(page,"\u274E")#quitar
                opc = await bot.wait_for_reaction(
                        ["\u25C0","\u25B6","\u2611","\u274E"],user=message.author,message=page,timeout=15)
                if not(opc):
                    for emoji in ["\u25C0","\u25B6","\u2611","\u274E"]:
                        try:
                            await bot.remove_reaction(page,emoji,
                                discord.member.utils.find(lambda m: m.id == "401391614838439936",
                                    message.channel.server.members
                                    )
                                )
                        except:
                            pass
                    return
                else:
                    emoji=opc.reaction.emoji
                    try:
                        await bot.remove_reaction(page,emoji,message.author)
                    except:
                        pass
                    if emoji=="\u25C0":
                        i=i-1
                        pass
                    elif emoji=="\u25B6":
                        i+=1
                        pass
                    elif emoji=="\u2611":
                        for e in ["\u25C0","\u25B6","\u2611","\u274E"]:
                            try:
                                await bot.remove_reaction(page,e,
                                    discord.member.utils.find(lambda m: m.id == "401391614838439936",
                                        message.channel.server.members
                                        )
                                    )
                            except:
                                pass
                        return
                    elif emoji=="\u274E":
                        await bot.delete_message(page)
                        return
            return

    await bot.process_commands(message) 


#Luis Albizo 13/01/18
