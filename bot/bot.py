import discord, random, time, re, datetime, os, threading, math, asyncio, socket, hashlib, base64
import pickle
from discord.ext import commands
from functools import reduce
from pymongo import MongoClient
from bot.banco import DIA, HORA, MINUTO
from .fortunas import fortunas
import bot.scraper as scraper
import bot.hchan as hchan
import bot.banco as banco
import bot.juegos as j

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
client = MongoClient()
db = client.laimbot
bank = banco.TBanco(db)
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
async def ss(ctx):
    if int(ctx.message.guild.id) == 301217828307075073:
        with open("bot/files/ss/"+random.choice(os.listdir("bot/files/ss")), "rb") as f:
            await bot.send_file(ctx.message.channel,f)
            f.close()
    else:
        await ctx.send("comando no disponible en este servidor")

@bot.command(pass_context=True)
async def siono(ctx):
    await ctx.send(random.choice(["Cy","\xf1o"]))

@bot.command(pass_context=True)
async def escoje(ctx):
    await ctx.send("Yo creo que " + random.choice(ctx.message.content.split(" ")[1:]))

@bot.command(pass_context=True)
async def dank(ctx):
    await ctx.send(":joy: :ok_hand:")

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
    msg = await bot.wait_for_message(author=message.author,timeout=15,check=lambda c: c.content[0]=='/')
    if not(msg):
        await bot.delete_message(fm)
        return
    await bot.delete_message(fm)
    response = scraper.goto_board(msg.content.strip())
    if response["error"]:
        fm = await ctx.send(response["content"])
        time.sleep(5)
        await bot.delete_message(fm)
        return
    else:
        fm = await ctx.send(response["content"][0])
        i=1
        hilos = list(response["content"][1])
        while True:
            el = hilos[i-1]
            page = await ctx.send(el)
            if i>1:
                await bot.add_reaction(page,"\u25C0")#anterior
            if i<15:
                await bot.add_reaction(page,"\u25B6")#siguiente
            await bot.add_reaction(page,"\u2611")#seleccionar
            await bot.add_reaction(page,"\u274E")#quitar
            opc = await bot.wait_for_reaction(
                    ["\u25C0","\u25B6","\u2611","\u274E"],user=message.author,message=page,timeout=15)
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
        page = await ctx.send("loading...")
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

@bot.command(pass_context=True)
async def hispa(ctx):
    global hchan
    message = ctx.message
    fm = await ctx.send(hchan.main_screen())
    msg = await bot.wait_for_message(author=message.author,timeout=35,check=lambda c: c.content[0]=='/')
    await bot.delete_message(fm)
    if not(msg):
        return
    response = hchan.goto_board(msg.content.strip())
    if response["error"]:
        fm = await ctx.send(response["content"])
        time.sleep(5)
        await bot.delete_message(fm)
        return
    else:
        fm = await ctx.send(response["content"][0])
        i=1
        hilos = list(response["content"][1])
        while True:
            el = hilos[i-1]
            page = await ctx.send(el)
            if i>1:
                await bot.add_reaction(page,"\u25C0")#anterior
            if i<13:
                await bot.add_reaction(page,"\u25B6")#siguiente
            await bot.add_reaction(page,"\u2611")#seleccionar
            await bot.add_reaction(page,"\u274E")#quitar
            opc = await bot.wait_for_reaction(
                    ["\u25C0","\u25B6","\u2611","\u274E"],user=message.author,message=page,timeout=45)
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
        imgs = list(hchan.get_thread_files(response["threads"][ids]["post_url"]))
        page = await ctx.send("Cargando...")
        while True:
            img = imgs[i]
            await bot.edit_message(page,(("Imagen %i de %i\n" % (i+1,len(imgs)))+img))
            if i>0:
                await bot.add_reaction(page,"\u25C0")#anterior
            else:
                try:
                    await bot.remove_reaction(page,"\u25C0",
                        discord.member.utils.find(lambda m: m.id == "401391614838439936",
                            message.channel.server.members
                        )
                    )
                except:
                    pass
            if i<len(imgs)-1:
                await bot.add_reaction(page,"\u25B6")#siguiente
            else:
                await bot.remove_reaction(page,"\u25B6",
                    discord.member.utils.find(lambda m: m.id == "401391614838439936",
                        message.channel.server.members
                    )
                )

            await bot.add_reaction(page,"\u2611")#seleccionar
            await bot.add_reaction(page,"\u274E")#quitar
            opc = await bot.wait_for_reaction(
                    ["\u25C0","\u25B6","\u2611","\u274E"],user=message.author,message=page,timeout=35)
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

@bot.command(pass_context=True)
async def t(ctx):
    """
    Comando para crear tags.

    Usa '_t test Hola Mundo' para crear o actualizar un tag
    Usa '_t test' para ver el contenido de un tag
    Usa '_t test *delete' para borrar un tag
    Usa '_t *list' para ver la lista de tags
    """
    cmd = re.compile(r"_t (?P<tag>\w+) ?(?P<content>.*)")
    t = cmd.match(ctx.message.content)
    if t:
        if t.groupdict()["content"] == "*delete":
            tags = db.accounts.find_one({'_id':int(ctx.message.author.id)},{'tags':True})
            if tags:
                if 'tags' in tags:
                    if t.groupdict()["tag"] in tags['tags']:
                        db.accounts.tags.find_one_and_delete({'_id':t.groupdict()["tag"]})
                        db.accounts.update_one({'_id':int(ctx.message.author.id)},
                            {'$pull':{'tags':t.groupdict()["tag"]}})
                        await ctx.send("Tag '%s' eliminado correctamente" % t.groupdict()["tag"])
                        return
            await ctx.send("Tu no puedes eliminar este tag")
        elif t.groupdict()["content"]:
            tags = db.accounts.find_one({'_id':int(ctx.message.author.id)},{'tags':True})
            if tags:
                if 'tags' in tags:
                    if t.groupdict()["tag"] in tags['tags']:
                        db.accounts.tags.update_one(
                            {'_id':t.groupdict()["tag"]},
                            {"$set":{"content":t.groupdict()["content"]}}
                        )
                        await ctx.send("Tag '%s' actualizado correctamente" % t.groupdict()["tag"])
                        return
                    else:
                        tag = db.accounts.tags.find_one({'_id':t.groupdict()["tag"]})
                        if not(tag):
                            db.accounts.tags.insert({'_id':t.groupdict()["tag"],
                            'content':t.groupdict()["content"]})
                            db.accounts.update_one({'_id':int(ctx.message.author.id)},
                                {'$push':{'tags':t.groupdict()["tag"]}})
                            await ctx.send("Tag '%s' creado correctamente." % t.groupdict()["tag"])
                        else:
                            return await ctx.send("Tu no puedes actualizar este tag")
            else:
                tag = db.accounts.tags.find_one({'_id':t.groupdict()["tag"]})
                if tag:
                    return await ctx.send("Tu no puedes actualizar este tag")
                else:
                    user = db.accounts.find_one({'_id':int(ctx.message.author.id)},{'_id':True})
                    if not(user):
                        db.accounts.insert_one(
                            {
                                '_id' : int(ctx.message.author.id),
                                'tags' : [t.groupdict()["tag"]]
                            }
                        )
                    db.accounts.tags.insert({'_id':t.groupdict()["tag"],'content':t.groupdict()["content"]})
                await ctx.send("Tag '%s' creado correctamente." % t.groupdict()["tag"])
        else:
            tag = db.accounts.tags.find_one({'_id':t.groupdict()["tag"]})
            if tag:
                await ctx.send(tag['content'])
            else:
                await ctx.send("No existe el tag '%s'" % t.groupdict()["tag"])
    elif ctx.message.content.lower() == "_t *list":
        tags = db.accounts.find_one({'_id':int(ctx.message.author.id)},{'tags':True})
        if tags:
            print(tags)
            if 'tags' in tags:
                l="```\n"
                for el in tags['tags']:
                    l+=el+"\n"
                return await ctx.send(l+"```")
        await ctx.send('No tienes ninguno')
    else:
        await ctx.send('Usa _help t')

#Luis Albizo 13/01/18
