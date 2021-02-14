import discord, random, time, re, datetime, os, threading, math, asyncio, socket, hashlib, base64
import pickle
from discord.ext import commands
from functools import reduce
from .fortunas import fortunas
import bot.scraper as scraper
import bot.hchan as hchan

MINUTO = 60
HORA = 60*MINUTO
DIA = 24*HORA

#Funciones utiles
def segundosV(segundos):
    dias = int(segundos/DIA)
    horas = int((segundos%DIA)/HORA)
    minutos = int((segundos%HORA)/MINUTO)
    segundos = segundos%MINUTO
    return {
        "dias" : dias,
        "horas" : horas,
        "minutos" : minutos,
        "segundos" : segundos
    }

#Bot
bot = commands.Bot(command_prefix="_")
dirbot = "./"
init_time = None

@bot.event
async def on_ready():
    global init_time
    print("Bot Online")
    init_time = int(time.time())

@bot.command(pass_context=True)
async def ping(ctx):
    """Testeando"""
    now = datetime.datetime.utcnow()
    delta = now-ctx.message.created_at
    await ctx.send(':ping_pong: Pong   ``%ims``' % delta.microseconds)

@bot.command(pass_context=True)
async def test(ctx):
    global init_time
    present_time = int(time.time())
    running_time = present_time - init_time
    running_time = segundosV(running_time)
    await ctx.send("Bot corriendo desde hace %i dias %i horas %i minutos y %i segundos :)" % (
        running_time["dias"],
        running_time["horas"],
        running_time["minutos"],
        running_time["segundos"]
        )
    )

@bot.command(pass_context=True)
async def echo(ctx):
    await ctx.send(ctx.message.content[6:])
    await ctx.message.delete()

@bot.command(pass_context=True)
async def quien(ctx):
    cmd = re.compile(r"_quien")
    def randomMember():
        mem=list(ctx.message.guild.members)
        return mem[random.randint(0,len(mem)-1)]
    m=""
    for el in cmd.split(ctx.message.content+" "):
        if el:
            m=m+randomMember().name+el
    await ctx.send(m)

@bot.command(pass_context=True)
async def siono(ctx):
    await ctx.send(random.choice(["Cy","\xf1o"]))

@bot.command(pass_context=True)
async def escoje(ctx):
    await ctx.send("Yo creo que " + random.choice(ctx.message.content.split(" ")[1:]))

@bot.command(pass_context=True)
async def fortuna(ctx):
    f=re.compile(r"_fortuna ?(?P<patron>.*)")
    pat=f.match(ctx.message.content).groupdict()["patron"]
    if pat:
        patf=re.compile(".*%s.*" % pat)
        for el in fortunas:
            if patf.match(el):
                await ctx.send(el)
                return
    elif int(ctx.message.guild.id) == 301217828307075073:
        await ctx.send(fortunas[random.randint(0,len(fortunas)-1)])
        return
    await ctx.send(fortunas[random.randint(0,len(fortunas)-3)])

@bot.command(pass_context=True)
async def chan(ctx):
    message = ctx.message
    fm = await ctx.send(scraper.main_screen())
    try:
        msg = await bot.wait_for("message", timeout=15,
            check=lambda m: m.content[0]=='/' and m.content[-1]=='/'
            and m.author==message.author)
    except asyncio.TimeoutError:
        await fm.delete()
        return
    await fm.delete()
    response = scraper.goto_board(msg.content.strip())
    if response["error"]:
        fm = await ctx.send(response["content"])
        time.sleep(5)
        await fm.delete()
        return
    else:
        fm = await ctx.send(response["content"][0])
        i=1
        hilos = list(response["content"][1])
        while True:
            el = hilos[i-1]
            page = await ctx.send(el)
            if i>1:
                await page.add_reaction("\u25C0")#anterior
            if i<15:
                await page.add_reaction("\u25B6")#siguiente
            await page.add_reaction("\u2611")#seleccionar
            await page.add_reaction("\u274E")#quitar
            try:
                opc, user = await bot.wait_for("reaction_add",
                    check = (lambda reaction, user:
                    reaction.emoji in 
                    ["\u25C0","\u25B6","\u2611","\u274E"] and 
                    user == message.author),
                    timeout=15)
            except asyncio.TimeoutError:
                await fm.delete()
                await page.delete()
                return
            await page.delete()
            if opc.emoji=="\u25C0":
                i-=1
                pass
            elif opc.emoji=="\u25B6":
                i+=1
                pass
            elif opc.emoji=="\u2611":
                break
            elif opc.emoji=="\u274E":
                await fm.delete()
                return
        await fm.delete()
        ids=i
        i=0
        imgs = list(scraper.get_thread_files(response["threads"][ids]["post_url"]))
        page = await ctx.send("loading...")
        while True:
            img = imgs[i]
            await page.edit(content=(("image %i of %i\n" % (i+1,len(imgs)))+img))
            if i>0:
                await page.add_reaction("\u25C0")#anterior
            if i<len(imgs)-1:
                await page.add_reaction("\u25B6")#siguiente
            await page.add_reaction("\u2611")#seleccionar
            await page.add_reaction("\u274E")#quitar
            try:
                opc, user = await bot.wait_for("reaction_add", check = (
                lambda reaction, user:
                reaction.emoji in ["\u25C0","\u25B6","\u2611","\u274E"]
                and user == message.author), timeout=15)
            except asyncio.TimeoutError:
                for emoji in ["\u25C0","\u25B6","\u2611","\u274E"]:
                    try:
                        await page.remove_reaction(emoji, bot.user)
                    except:
                        pass
                return
            emoji=opc.emoji
            try:
                await page.remove_reaction(emoji,message.author)
            except:
                pass
            if emoji=="\u25C0":
                i=i-1
                if not(i):
                    await page.remove_reaction(emoji, bot.user)
                pass
            elif emoji=="\u25B6":
                i+=1
                if i==len(img)-1:
                    await page.remove_reaction(emoji, bot.user)
                pass
            elif emoji=="\u2611":
                for e in ["\u25C0","\u25B6","\u2611","\u274E"]:
                    try:
                        await page.remove_reaction(e, bot.user)
                    except:
                        pass
                return
            elif emoji=="\u274E":
                await page.delete()
                return
        return

@bot.command(pass_context=True)
async def hispa(ctx):
    global hchan
    message = ctx.message
    fm = await ctx.send(hchan.main_screen())
    try:
        msg = await bot.wait_for("message", timeout=35, check=lambda c: c.content[0]=='/' and c.content[-1]=='/' and c.author == message.author)
        await fm.delete()
    except asyncio.TimeoutError:
        await fm.delete()
        return
    response = hchan.goto_board(msg.content.strip())
    if response["error"]:
        fm = await ctx.send(response["content"])
        time.sleep(5)
        await fm.delete()
        return
    else:
        fm = await ctx.send(response["content"][0])
        i=1
        hilos = list(response["content"][1])
        while True:
            el = hilos[i-1]
            page = await ctx.send(el)
            if i>1:
                await page.add_reaction("\u25C0")#anterior
            if i<13:
                await page.add_reaction("\u25B6")#siguiente
            await page.add_reaction("\u2611")#seleccionar
            await page.add_reaction("\u274E")#quitar
            try:
                opc, user = await bot.wait_for("reaction_add", check=lambda
                    reaction, user: reaction.emoji in
                    ["\u25C0","\u25B6","\u2611","\u274E"] and
                    user == message.author,
                    timeout=45)
            except asyncio.TimeoutError:
                await fm.delete()
                await page.delete()
                return
            await page.delete()
            if opc.emoji=="\u25C0":
                i-=1
                pass
            elif opc.emoji=="\u25B6":
                i+=1
                pass
            elif opc.emoji=="\u2611":
                break
            elif opc.emoji=="\u274E":
                return
        await fm.delete()
        ids=i
        i=0
        imgs = list(hchan.get_thread_files(response["threads"][ids]["post_url"]))
        page = await ctx.send("Cargando...")
        while True:
            img = imgs[i]
            await page.edit(content=(("Imagen %i de %i\n" % (i+1,len(imgs)))+img))
            if i>0:
                await page.add_reaction("\u25C0")#anterior
            else:
                try:
                    await page.remove_reaction("\u25C0", bot.user)
                except:
                    pass
            if i<len(imgs)-1:
                await page.add_reaction("\u25B6")#siguiente
            else:
                await page.remove_reaction("\u25B6", bot.user)
            await page.add_reaction("\u2611")#seleccionar
            await page.add_reaction("\u274E")#quitar
            try:
                opc, user = await bot.wait_for("reaction_add", check=lambda
                        reaction, user: reaction.emoji in 
                        ["\u25C0","\u25B6","\u2611","\u274E"] and
                        user == message.author,timeout=15)
            except asyncio.TimeoutError:
                for emoji in ["\u25C0","\u25B6","\u2611","\u274E"]:
                    try:
                        await page.remove_reaction(emoji, bot.user)
                    except:
                        pass
                return
            emoji=opc.emoji
            try:
                await page.remove_reaction(emoji, message.author)
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
                        await page.remove_reaction(e, bot.user)
                    except:
                        pass
                return
            elif emoji=="\u274E":
                await page.delete()
                return
        return

get_id = lambda ctx: int(ctx.message.author.id)

#Luis Albizo 13/01/18
