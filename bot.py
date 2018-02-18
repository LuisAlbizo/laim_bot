import discord, async, random, time, sqlite3, re, datetime, os, threading, math, asyncio, socket, hashlib
import base64
from discord.ext import commands
from .fortunas import fortunas
from functools import reduce
import bot.scraper as scraper
import bot.hchan as hchan
import bot.banco as banco
import bot.juegos as j

#Funciones utiles
def segundosV(segundos):
    dias = 0
    horas = 0
    minutos = 0
    segundos = segundos
    while segundos >= 60:
        minutos+=1
        segundos-=60
    while minutos >= 60:
        horas+=1
        minutos-=60
    while horas >= 24:
        dias+=1
        horas-=24
    return {
        "dias" : dias,
        "horas" : horas,
        "minutos" : minutos,
        "segundos" : segundos
    }

#Bot
bot = commands.Bot(command_prefix="_")
dirbot = "/sdcard/practicas/python/discord/laimbot/bot/"
dbf = "bot/files/laim.db"
dbt = "bot/files/laimtest.db"
bank = banco.TBanco(dbt)
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
    delta = now-ctx.message.timestamp
    await bot.say(':ping_pong: Pong   ``%ims``' % delta.microseconds)

@bot.command(pass_context=True)
async def susurro(ctx):
    await bot.whisper("Test")

@bot.command(pass_context=True)
async def cn(ctx):
    try:
        await bot.edit_profile(username=ctx.message.content[4:])
    except:
        await bot.say("Rate limit error")
    await bot.delete_message(ctx.message)

@bot.command(pass_context=True)
async def test(ctx):
    global init_time
    present_time = int(time.time())
    running_time = present_time - init_time
    running_time = segundosV(running_time)
    await bot.say("Bot corriendo desde hace %i dias %i horas %i minutos y %i segundos :)" % (
        running_time["dias"],
        running_time["horas"],
        running_time["minutos"],
        running_time["segundos"]
        )
    )

@bot.command(pass_context=True)
async def echo(ctx):
    await bot.say(ctx.message.content[6:])
    await bot.delete_message(ctx.message)

@bot.command(pass_context=True)
async def quien(ctx):
    cmd = re.compile(r"_quien")
    def randomMember():
        mem=list(ctx.message.server.members)
        return mem[random.randint(0,len(mem)-1)]
    m=""
    for el in cmd.split(ctx.message.content+" "):
        if el:
            m=m+randomMember().name+el
    await bot.say(m)

@bot.command(pass_context=True)
async def ss(ctx):
    if int(ctx.message.server.id) == 301217828307075073:
        with open("bot/files/ss/"+random.choice(os.listdir("bot/files/ss")), "rb") as f:
            await bot.send_file(ctx.message.channel,f)
            f.close()
    else:
        await bot.say("comando no disponible en este servidor")

@bot.command(pass_context=True)
async def siono(ctx):
    await bot.say(random.choice(["Cy","\xf1o"]))

@bot.command(pass_context=True)
async def escoje(ctx):
    await bot.say("Yo creo que " + random.choice(ctx.message.content.split(" ")[1:]))

@bot.command(pass_context=True)
async def dank(ctx):
    await bot.say(":joy: :ok_hand:")

@bot.command(pass_context=True)
async def amigos(ctx):
    with open('bot/files/amigos2017final.png', 'rb') as f:
        await bot.send_file(ctx.message.channel, f)
        f.close()

@bot.command(pass_context=True)
async def fortuna(ctx):
    f=re.compile(r"_fortuna ?(?P<patron>.*)")
    pat=f.match(ctx.message.content).groupdict()["patron"]
    if pat:
        patf=re.compile(".*%s.*" % pat)
        for el in fortunas:
            if patf.match(el):
                await bot.say(el)
                return
    elif int(ctx.message.server.id) == 301217828307075073:
        await bot.say(fortunas[random.randint(0,len(fortunas)-1)])
        return
    await bot.say(fortunas[random.randint(0,len(fortunas)-3)])


@bot.command(pass_context=True)
async def screenshot(ctx):
    """_screenshot <url> (la url de la pagina a tomar screenshot)"""
    url=re.compile(r"_screenshot (?P<url>.+)")
    url=url.match(ctx.message.content)
    if not(url):
        return await bot.say("Usa _help screenshot")
    url=url.groupdict()["url"]
    if len(url)>300:
        return await bot.say("No puedes usar mas de 300 caracteres")
    conn = socket.socket()
    try:
        conn.connect(("127.0.0.1",4300))
    except:
        return await bot.say("Servicio no disponible ;_;")
    idph = eval("0x"+hashlib.sha1(("%s %s" % (ctx.message.author.name,url)).encode()).hexdigest())
    os.system("mkdir %sfiles/ph/%i" % (dirbot,idph))
    conn.send(("ss %s %sfiles/ph/%i/screenshot.png" % (
            base64.b64encode(url.encode()).decode(),
            dirbot,
            idph
        )).encode()
    )
    resp = conn.recv(1024).decode().split(":")
    conn.close()
    if resp[0]=="succes":
        with open("%sfiles/ph/%i/screenshot.png" % (dirbot,idph),"rb") as f:
            await bot.send_file(ctx.message.channel,f)
            f.close()
    else:
        await bot.say("Error: "+resp[1])
    os.system("rm -r %sfiles/ph/%i/" % (dirbot,idph))

@bot.command(pass_context=True)
async def meme(ctx):
    """
    Comando para hacer memes frescos.

    _meme top text|bottom text
    (incluye la imagen en tu mensaje)
    _meme https://www.ejemplo.com/imagen.jpg top|bottom
    (o el link)

    Para personalizar mas el resultado
    _meme test[[color: #f9a; font-size: 50px]]|test2[[color:#456; margin-bottom: 80px]] {{width: 500px; height: 700px;}}
    Despues del texto entre dobles corchetes cuadrados ([[]]) escribe estilo css
    Y despues de ambos textos escribe entre dobles corchetes ({{}}) estilo css para el meme en general

    """
    pass


@bot.command(pass_context=True)
async def chan(ctx):
    message = ctx.message
    fm = await bot.send_message(message.channel,scraper.main_screen())
    msg = await bot.wait_for_message(author=message.author,timeout=15,check=lambda c: c.content[0]=='/')
    if not(msg):
        await bot.delete_message(fm)
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

@bot.command(pass_context=True)
async def hispa(ctx):
    global hchan
    message = ctx.message
    fm = await bot.send_message(message.channel,hchan.main_screen())
    msg = await bot.wait_for_message(author=message.author,timeout=35,check=lambda c: c.content[0]=='/')
    await bot.delete_message(fm)
    if not(msg):
        return
    response = hchan.goto_board(msg.content.strip())
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
        page = await bot.send_message(message.channel,"Cargando...")
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
    cmd = re.compile(r"_t (?P<tag>\w+) ?(?P<content>.*)")
    t = cmd.match(ctx.message.content)
    if t:
        db = sqlite3.connect(dbf)
        if t.groupdict()["content"] == "*delete":
            cur = db.execute("SELECT user FROM Tags WHERE tag IS '%s'" % t.groupdict()["tag"])
            try:
                user = next(cur)[0]
                if int(ctx.message.author.id) == user:
                    db.execute("DELETE FROM Tags WHERE tag IS '%s'" % t.groupdict()["tag"])
                    db.commit()
                    await bot.say("Tag '%s' eliminado correctamente" % t.groupdict()["tag"])
                else:
                    await bot.say("Tu no puedes eliminar este tag")
            except:
                await bot.say("Ese tag ni existe we")
        elif t.groupdict()["content"]:
            cur = db.execute("SELECT user FROM Tags WHERE tag IS '%s'" % t.groupdict()["tag"])
            try:
                user = next(cur)[0]
                if int(ctx.message.author.id) == user:
                    db.execute("UPDATE Tags SET content = '%s' WHERE tag IS '%s'" % (
                        t.groupdict()["content"],
                        t.groupdict()["tag"]
                        )
                    )
                    db.commit()
                    await bot.say("Tag '%s' actualizado correctamente" % t.groupdict()["tag"])
                else:
                    await bot.say("Tu no puedes actualizar este tag")
            except:
                db.execute("INSERT INTO Tags VALUES ('%s','%s',%i)" % (
                    t.groupdict()["tag"],
                    t.groupdict()["content"],
                    int(ctx.message.author.id)
                    )
                )
                db.commit()
                await bot.say("Tag '%s' creado correctamente." % t.groupdict()["tag"])
        else:
            cur = db.execute("SELECT content FROM Tags WHERE tag IS '%s'" % t.groupdict()["tag"])
            try:
                content = next(cur)[0]
                await bot.say(content)
                cur.close()
            except:
                await bot.say("No existe el tag '%s'" % t.groupdict()["tag"])
        db.close()      
    elif ctx.message.content.strip().lower() == "_t *list":
        db = sqlite3.connect(dbf)
        cur = db.execute("SELECT tag FROM Tags ORDER BY user")
        l="```\n"
        for el in cur:
            l+=el[0]+"\n"
        await bot.say(l+"```")
        db.close()
    else:
        await bot.say("""No, asi no funciona
            ```
Usa '_t test Hola Mundo' para crear o actualizar un tag
Usa '_t test' para ver el contenido de un tag
Usa '_t test *delete' para borrar un tag
Usa '_t *list' para ver la lista de tags
            ```
            """)

#Comandos banco

@bot.command(pass_context=True)
async def reward(ctx):
    db = sqlite3.connect(dbt)
    db.execute("CREATE TABLE IF NOT EXISTS Rewards(User INTEGER PRIMARY KEY NOT NULL, Last INTEGER, Unica BOOLEAM NOT NULL,init INTEGER NOT NULL)")
    db.commit()
    cur=db.execute("SELECT * FROM Rewards WHERE User IS %i" % int(ctx.message.author.id))
    try:
        r=next(cur)
        cur.close()
        if ctx.message.content[8:].strip().lower()=="-u":
            if r[2]:
                await bot.say("Ya recojiste tu recompensa unica :'(")
            else:
                await bot.say("")
        else:
            if int(time.time())-r[1]>=banco.DIA:
                db.execute("UPDATE Rewards SET Last = %i WHERE User IS %i" % (
                    int(time.time()),int(ctx.message.author.id)
                    )
                )
                db.commit()
                c=bank.obtenerCuenta(int(ctx.message.author.id))
                nm=banco.TMoneda(100,banco.DIA,banco.makeID(dbt))
                c.agregarMoneda(nm)
                c.actualizarSaldo()
                s=segundosV(nm.consultarExpiracion())
                await bot.say("Recompensa obtenida:\n```\n%s:{\n\tduracion: %i dias,%i horas,%i minutos\
                        \n\tvalor: %i\n}```" % (
                        hex(nm.getID())[2:].upper(),
                        s["dias"],
                        s["horas"],
                        s["minutos"],
                        nm.consultarValor()
                    ),
                    delete_after=10.0
                )
            else:
                s=segundosV(banco.DIA-((int(time.time())-r[1])))
                await bot.say("Recompensa disponible dentro de %i horas, %i minutos y %i segundos" %
                        (
                            s["horas"],
                            s["minutos"],
                            s["segundos"]
                        )
                    )
    except:
        c=bank.crearCuenta(int(ctx.message.author.id))
        db.execute("INSERT INTO Rewards VALUES (%i, %i, 0, %i)" % (
            int(ctx.message.author.id),
            int(time.time()),
            int(time.time())
            )
        )
        db.commit()
        for m in c.__json__()["saldo_monedas"]:
            s=segundosV(m["expiracion"])
            await bot.say("Recompensa obtenida por crear una cuenta:\
                \n```\n%s:{\n\tduracion: %i dias,%i horas,%i minutos\n\tvalor: %i\n}```" % (
                hex(m["ID"])[2:].upper(),
                s["dias"],
                s["horas"],
                s["minutos"],
                m["valor"]
            ),
            delete_after=16.0
        )
        nm=banco.TMoneda(100,banco.DIA,banco.makeID(dbt))
        c.agregarMoneda(nm)
        c.actualizarSaldo()
        s=segundosV(nm.consultarExpiracion())
        await bot.say("Recompensa obtenida:\n```\n%s:{\n\tduracion: %i dias,%i horas,%i minutos\n\tvalor: %i\n}```" % (
                hex(nm.getID())[2:].upper(),
                s["dias"],
                s["horas"],
                s["minutos"],
                nm.consultarValor()
            ),
            delete_after=16.0       
        )
    finally:
        db.close()

@bot.command(pass_context=True)
async def saldo(ctx):
    c=bank.obtenerCuenta(int(ctx.message.author.id))
    if c and ctx.message.content.lower()[7:]=="-verbo":
        c.actualizarSaldo()
        for m in c.__json__()["saldo_monedas"]:
            s=segundosV(m["expiracion"])
            await bot.say("\n```\n%s:{\n\tduracion: %i dias,%i horas,%i minutos\n\tvalor: %i\n}```" % (
                hex(m["ID"])[2:].upper(),
                s["dias"],
                s["horas"],
                s["minutos"],
                m["valor"]
            ),
            delete_after=16.0
        )
    elif c:
        c.actualizarSaldo()
        s=segundosV(sum([m.consultarExpiracion() for m in c.getSaldo("monedas")]))
        await bot.say("**%s:** Valor total: %i, Duracion conjunta: %s"  % (
            ctx.message.author.name,
            c.getSaldo("valor"),
            ("%i dias, %i horas y %i minutos" % (s["dias"],s["horas"],s["minutos"]))
            )
        )
    else:
        await bot.say("Primero crea tu cuenta con _reward")

@bot.command(pass_context=True)
async def top(ctx):
    def insOrd(l,x,comp):
        if l==list():
            return [x]
        elif comp(x,l[0]):
            return [x]+l
        else:
            return [l[0]]+insOrd(l[1:],x,comp)
    def Ord(l,comp):
        if l==list():
            return list()
        else:
            return insOrd(Ord(l[1:],comp),l[0],comp)
    param=ctx.message.content[5:]
    cuentas=[]
    carga = await bot.send_message(ctx.message.channel,"*Obteniendo cuentas...*")
    for member in ctx.message.server.members:
        c=bank.obtenerCuenta(int(member.id))
        if c:
            threading.Thread(target=c.actualizarSaldo).start()
            cuentas.append(c)
    print([el.getID() for el in cuentas])
    param=param.split(' ')
    try:
        if len(cuentas)<int(param[0]):
            ma=len(cuentas)
        else:
            ma=int(param[0])
    except:
        if len(cuentas)<10:
            ma=len(cuentas)
        else:
            ma=10
    if len(param)>1:
        tipo=param[1]
    else:
        tipo="valor"
    await bot.edit_message(carga,"*Definiendo top...*")
    if tipo=="tiempo":
        top=Ord(cuentas,lambda x,y:sum(
            [m.consultarExpiracion() for m in x.getSaldo("monedas")])>=sum(
            [m.consultarExpiracion() for m in y.getSaldo("monedas")]
            )
        )
    else:
        top=Ord(cuentas,lambda x,y:x.getSaldo("valor")>=y.getSaldo("valor"))
    timestamp=time.localtime()
    timestamp="%i/%i/%i %i:%i:%i" % (
        timestamp.tm_mday,
        timestamp.tm_mon,
        timestamp.tm_year,
        timestamp.tm_hour,
        timestamp.tm_min,
        timestamp.tm_sec
    )
    await bot.edit_message(carga,"*Generando top...*")
    topStr="**Top __%s__ - %s (%s)**\n```\n" % (ctx.message.server.name,timestamp,tipo)
    i=1
    while i<=ma:
        u=discord.member.utils.find(lambda m: int(m.id) == top[i-1].getID(),ctx.message.server.members)
        topStr+="[%i] - %s (%i Valor total, %.2f Tiempo total en dias)\n" % (
            i,
            u.name,
            top[i-1].getSaldo("valor"),
            sum([m.consultarExpiracion() for m in top[i-1].getSaldo("monedas")])/60/60/24
        )
        i+=1
    await bot.delete_message(carga)
    await bot.send_message(ctx.message.channel,topStr+"```")

@bot.command(pass_context=True)
async def cambio(ctx):
    cbio=re.compile(r"_cambio (?P<ids>([0-9A-Fa-f]{1,6}:?)+) ?(?P<modo>[tvTV])\w*")
    cbio=cbio.fullmatch(ctx.message.content)
    if cbio:
        cuenta=bank.obtenerCuenta(int(ctx.message.author.id))
        if not(cuenta):
            return await bot.say("Primero crea una cuenta con _reward")
        cbio=cbio.groupdict()
        ids=[eval("0x"+idd) for idd in cbio["ids"].split(":")]
        for m in ids:
            moneda=cuenta.obtenerMoneda(m)
            if moneda:
                succ,nmoneda=banco.TCambio(moneda,cbio["modo"].lower())
                if not(succ):
                    await bot.say("Error: "+nmoneda)
                else:
                    cuenta.eliminarMoneda(moneda.getID())
                    cuenta.agregarMoneda(nmoneda)
                    cuenta.actualizarSaldo()
                    m=cuenta.obtenerMoneda(nmoneda.getID()).__json__()
                    s=segundosV(m["expiracion"])
                    await bot.say(
                        "\n```\nNueva %s:{\n\tduracion: %i dias,%i horas,%i minutos\n\tvalor: %i\n}```" % (
                        hex(m["ID"])[2:].upper(),
                        s["dias"],s["horas"],s["minutos"],
                        m["valor"]
                        )
                    )
            else:
                await bot.say("La moneda %s no te pertenece" % hex(m)[2:].upper())
    else:
        await bot.say("**Uso: '_cambio id modo' donde id es la id de la moneda y modo es 't' o 'v'**\n"+
        "*V si quieres multiplicar el valor de la moneda por 10 y dividir su tiempo en 2*\n"+
        "*T si quieres multiplicar el tiempo de tu moneda por 10 pero dividir su tiempo entre 2*")

@bot.command(pass_context=True)
async def cambiovalor(ctx):
    cbio=re.compile(r"_cambiovalor (?P<ids>([0-9A-Fa-f]{1,6}:?)+) (?P<valor>10*)")
    cbio=cbio.fullmatch(ctx.message.content)
    if cbio:
        cuenta=bank.obtenerCuenta(int(ctx.message.author.id))
        if not(cuenta):
            return await bot.say("Primero crea una cuenta con _reward")
        cbio=cbio.groupdict()
        ids=[eval("0x"+idd) for idd in cbio["ids"].split(":")]
        valor=int(cbio["valor"])
        for m in ids:
            moneda=cuenta.obtenerMoneda(m)
            if moneda:
                while True:
                    if moneda.consultarValor()==valor:
                        break
                    elif valor>moneda.consultarValor():
                        succ,moneda=banco.TCambio(moneda,"v")
                    else:
                        succ,moneda=banco.TCambio(moneda,"t")
                    if not(succ):
                        await bot.say("(%s) Error: %s" % (hex(moneda.getID())[2:].upper(),nmoneda))
                    else:
                        cuenta.eliminarMoneda(moneda.getID())
                        cuenta.agregarMoneda(moneda)
                        m=cuenta.obtenerMoneda(moneda.getID()).__json__()
                        s=segundosV(m["expiracion"])
                        await bot.say(
                        "\n```\nNueva %s:{\n\tduracion: %i dias,%i horas,%i minutos\n\tvalor: %i\n}```" % (
                        hex(m["ID"])[2:].upper(),
                        s["dias"],s["horas"],s["minutos"],
                        m["valor"]
                            )
                        )
            else:
                await bot.say("La moneda %s no te pertenece" % hex(m)[2:].upper())
        cuenta.actualizarSaldo()
    else:
        await bot.say("**Uso: '_cambio id1:id2:..:idN valor' donde id es la id de las monedas y un valor**")

@bot.command(pass_context=True)
async def cuenta(ctx):
    """
    Comando para ver informacion de una cuenta:
        *saldo:
            muestra saldo
        *monedas:
            muestra todas las monedas de la cuenta
    """
    mention = re.search(r"<@\d{18}>",ctx.message.content)
    if mention:
        mention = mention.group()
        user = discord.member.utils.find(lambda m: m.id == mention[2:-1],
            ctx.message.channel.server.members
        )
        if user:
            cuenta=bank.obtenerCuenta(int(mention[2:-1]))
            if not(cuenta):
                return await bot.say("El usuario no tiene cuenta")
        else:
            return await bot.say("Usuario no encontrado")
    else:
        mention=ctx.message.author.mention
        cuenta=bank.obtenerCuenta(int(ctx.message.author.id))
        if not(cuenta):
            return await bot.say("Primero crea una cuenta con _reward")
    param = re.match(r"_cuenta (<@\d{18}>)* ?\*(?P<param>\w+)",ctx.message.content)
    cuenta.actualizarSaldo()
    if param:
        param = param.groupdict()["param"]
        if param == "monedas":
            for m in cuenta.__json__()["saldo_monedas"]:
                s=segundosV(m["expiracion"])
                await bot.say("\n```\n%s:{\n\tduracion: %i dias,%i horas,%i minutos\n\tvalor: %i\n}```" % (
                    hex(m["ID"])[2:].upper(),
                    s["dias"],
                    s["horas"],
                    s["minutos"],
                    m["valor"]
                    )
                )
        else:
            await bot.say("Parametro incorrecto")
        return
    timestamp=time.localtime()
    timestamp="%i/%i/%i %i:%i:%i" % (
        timestamp.tm_mday,
        timestamp.tm_mon,
        timestamp.tm_year,
        timestamp.tm_hour,
        timestamp.tm_min,
        timestamp.tm_sec
    )
    info = "%s:(%s)\n```\n" % (mention,timestamp)
    monedas = [m for m in cuenta.getSaldo("monedas")]
    s=segundosV(int(time.time())-cuenta.getCreacion())
    info += "\tCuenta creada hace: %i dias, %i horas, %i minutos y %i segundos \n" % (
        s["dias"],
        s["horas"],
        s["minutos"],
        s["segundos"]
    )
    info += "\tMonedas: %i\n" % len(monedas)
    info += "\tSaldo: %i \n" % cuenta.getSaldo("valor")
    duracion = sum([m.consultarExpiracion() for m in  cuenta.getSaldo("monedas")])
    info += "\tDuracion: %.2f dias \n" % (duracion/60/60/24)
    if not(monedas):
        return await bot.say(info+"```")
    mduracion = max(monedas,key=lambda x:x.consultarExpiracion())
    info += "\tMoneda con mayor duracion: %s (%i,%.2f dias)\n" % (
        hex(mduracion.getID())[2:].upper(),
        mduracion.consultarValor(),
        mduracion.consultarExpiracion()/60/60/24
    )
    mduracion = min(monedas,key=lambda x:x.consultarExpiracion())
    info += "\tMoneda con menor duracion: %s (%i,%.2f dias)\n" % (
        hex(mduracion.getID())[2:].upper(),
        mduracion.consultarValor(),
        mduracion.consultarExpiracion()/60/60/24
    )
    dpromedio = segundosV(int(duracion)/len(monedas))
    info += "\tDuracion promedio: %i dias, %i horas, %i minutos y %i segundos\n" % (
        dpromedio["dias"],
        dpromedio["horas"],
        dpromedio["minutos"],
        dpromedio["segundos"]
    )
    await bot.say(info+"```")
    await bot.say(":".join([hex(m.getID())[2:].upper() for m in monedas]))

@bot.command(pass_context=True)
async def juntar(ctx):
    """
    Comando para fusionar monedas
    Las monedas deben tener el mismo valor

    Ejemplo:
        _juntar FF:FA:1A:10
    """
    ids = re.compile(r"_juntar (?P<ids>([0-9A-Fa-f]{1,6}:?)+)")
    match = ids.match(ctx.message.content)
    if match:
        ids=match.groupdict()["ids"].split(":")
        if len(ids)<2:
            return await bot.say("No puedes fusionar menos de 2 monedaa")
    else:
        return await bot.say("Formato incorrecto, usa _help juntar")
    cuenta = bank.obtenerCuenta(int(ctx.message.author.id))
    print(ids)
    if not(cuenta):
        return await bot.say("Primero crea una cuenta con _reward")
    monedas = [cuenta.obtenerMoneda(eval("0x"+str(mid))) for mid in ids]
    if not(monedas):
        return await bot.say("Ninguna de esas monedas te pertenece")
    valor = monedas[0].consultarValor()
    if not(all([m.consultarValor()==valor for m in monedas])):
        return await bot.say("Las monedas tienen valores distintos")
    for m in monedas:
        cuenta.eliminarMoneda(m.getID())
        banco.deleteID(m.getID(),dbt)
    nmoneda = banco.FusionarMonedas(monedas,banco.makeID(dbt))
    cuenta.agregarMoneda(nmoneda)
    cuenta.actualizarSaldo()
    m=cuenta.obtenerMoneda(nmoneda.getID()).__json__()
    s=segundosV(m["expiracion"])
    await bot.say(
        "\n```\nNueva %s:{\n\tduracion: %i dias,%i horas,%i minutos\n\tvalor: %i\n}```" % (
        hex(m["ID"])[2:].upper(),
        s["dias"],s["horas"],s["minutos"],
        m["valor"]
        )
    )

@bot.command(pass_context=True)
async def dividir(ctx):
    """
    Comando para dividir monedas
    Las monedas deben durar mas de 2 minutos

    Ejemplo:
        _dividir FF:FA:1A:10
    """
    ids = re.compile(r"_dividir (?P<ids>([0-9A-Fa-f]{1,6}:?)+) ?(?P<div>\d+)")
    match = ids.match(ctx.message.content)
    if match:
        ids=ids.groupdict()["ids"]
    else:
        return await bot.say("Formato incorrecto, usa _help dividir")

#Comandos para juego

@bot.command(pass_context=True)
async def blackjack(ctx):
    """
    Juega a blackjack usando '_blackjack FF' FF es la ID de la moneda que vas a apostar y su valor se dividira para tener mas fichas.
        Ejemplo, si tu moneda vale 100 tendras 100 fichas que apostar, cada ficha es una division de la moneda asi que dura 4 veces mas que esta.
        Al salir del juego no se te regresaran las fichas, se uniran en las menores fichas posibles y duraran lo que originalmente duraba tu moneda.

    Informacion de la casa:
        Blackjack se paga 3 a 1
        Victoria se paga 2 a 1
        Seguro se paga 1 a 1
        21 con tres 7's se paga 10 a 2 (tendras que apostar el doble de tu apuesta inical si tus dos primeras cartas son 7's)
        Se usan 6 masos (no se escojen valores aleatorios o cartas de un solo maso y las cartas se van yendo del juego)
        Dealer pide con 16 y se mantiene con 17
    """
    canal = ctx.message.channel
    try:
        params=ctx.message.content.split("_blackjack ")[1].split(" ")
    except IndexError:
        await bot.say("Tienes que apostar una moneda para empezar a jugar\nEjemplo:  *_blackjack FFF 10*")
        return
    c=bank.obtenerCuenta(int(ctx.message.author.id))
    if re.fullmatch(r"[0-9a-f]+",params[0].lower()):
        moneda = c.obtenerMoneda(eval("0x"+params[0]))
        if not(moneda):
            await bot.say("La moneda %s no te pertenece." % params[0])
            return
    else:
        await bot.say("ID de moneda no valida: "+params[0])
        return
    div=int(moneda.consultarValor())
    if len(params)>1:
        if re.fullmatch(r"10+",params[1]):
            div=int(params[1])
    msg = await bot.say("Dividiendo %s entre %i..." % (params[0],div))
    if moneda.consultarValor()<div:
        await bot.edit_message(msg,
        "No se puede dividir la moneda %s entre %i, solo vale %i" % (
                params[0],
                div,
                moneda.consultarValor()
            )
        )
        return
    monedas=[]
    await bot.say("Nueva ronda",delete_after=2.0)
    for el in range(div):
        _,nmoneda = banco.TCambio(banco.ClonarMoneda(moneda),"t")
        for el in range(int(math.log10(div))-1):
            _,nmoneda = banco.TCambio(nmoneda,"t")
        monedas.append(nmoneda)
    rp = j.Repartidor(j.masobj)
    await bot.delete_message(msg)
    info = await bot.send_message(canal,"Cargando info...")
    await bot.edit_message(info,"**Fichas: %i**\n**Tiempo de cada ficha: %.2f (horas)**" % (
        len(monedas),monedas[0].consultarExpiracion()/60/60
    ))
    ronda = await bot.send_message(canal,"...")
    while True:
        apuestm = await bot.say("Cuanto quieres apostar? (escribe un numero de fichas del 1 al " + str(len(monedas)))
        while True:
            apuesta = await bot.wait_for_message(channel=canal,author=ctx.message.author,
                check=lambda x: x.content.isdigit(),timeout=30)
            if not(apuesta):
                await bot.delete_message(apuestm)
                await bot.delete_message(info)
                #regresar las fichas
                return
            await bot.delete_message(apuesta)
            apuestc = int(apuesta.content)
            if apuestc>len(monedas):
                await bot.say("No tienes tantas fichas, di otro numero",delete_after=6.0)
            else:
                monedas=monedas[apuestc:]
                await bot.edit_message(info,"**Fichas: %i**\n**Tiempo de cada ficha: %.2f (horas)**" % (
                    len(monedas),nmoneda.consultarExpiracion()/60/60
                ))
                break
        await bot.delete_message(apuestm)
        await bot.edit_message(info,"**Fichas: %i**\n**Tiempo de cada ficha: %.2f (horas)**" % (
            len(monedas),nmoneda.consultarExpiracion()/60/60
        ))
        jugador=j.bjrepartir(rp.repartir(2))
        dealer=j.bjrepartir(rp.repartir(2))
        opc = "```\nDealer tiene: [%s (%i)]\nTu tienes: {%s, %s (%i)}\n\nOpciones: doblar, pedir, mantener, salir" % (
            dealer["cartas"][0]+", ?",
            max(j.valores[dealer["cartas"][0][0]]),
            jugador["cartas"][0],
            jugador["cartas"][1],
            max(filter(lambda x:x<=21,jugador["valores"]))
        )
        dividir, _777 = False, False
        if j.valores[jugador["cartas"][0][0]] == j.valores[jugador["cartas"][1][0]]:
            pass
            opc+=", dividir"
            dividir=True
        if jugador["cartas"][0][0] == "7" and jugador["cartas"][1][0] == "7":
            opc+=", 777"
            _777=True
        await bot.edit_message(ronda,opc+"\n```")
        if dealer["cartas"][0][0]=="A":
            seguroq=await bot.say("Apuestas por seguro? (si/no)")
            opcion = await bot.wait_for_message(channel=canal,author=ctx.message.author,timeout=10)
            if not(opcion):
                seguro = False
            else:
                await bot.delete_message(seguroq)
                seguro = False
                if opcion.content.split(' ')[0].lower() == "si":
                    seguro = True
                await bot.delete_message(opcion)
            if seguro:
                if len(monedas)<apuestc:
                    await bot.say("No tienes suficientes fichas para apostar por seguro",delete_after=6.0)
                    seguro = False
                else:
                    monedas=monedas[apuestc:]
                    await bot.edit_message(info,"**Fichas: %i**\n**Tiempo de cada ficha: %.2f (horas)**" % (
                        len(monedas),nmoneda.consultarExpiracion()/60/60
                    ))
            if j.valores[dealer["cartas"][0][0]]==[10]:
                if seguro:
                    monedas+=[banco.ClonarMoneda(nmoneda) for i in range(apuestc*2)]
                    await bot.edit_message(info,"**Fichas: %i**\n**Tiempo de cada ficha: %.2f (horas)**" % (
                        len(monedas),nmoneda.consultarExpiracion()/60/60
                    ))
                    if 21 in jugador["valores"]:
                        monedas+=[banco.ClonarMoneda(nmoneda) for i in range(apuestc)]
                        await bot.edit_message(info,
                        "**Fichas: %i**\n**Tiempo de cada ficha: %.2f (horas)**" % (
                            len(monedas),nmoneda.consultarExpiracion()/60/60
                        ))
                continue
        while True:
            opcion = await bot.wait_for_message(channel=canal,author=ctx.message.author,timeout=30)
            if not(opcion):
                await bot.delete_message(info)
                await bot.delete_message(ronda)
                #regresar fichas
                return
            else:
                await bot.delete_message(opcion)
                opcion = opcion.content.split(' ')[0].lower()
                break
        ploses=False
        if opcion == "salir":
            break
        elif opcion == "mantener":
            pass
        elif opcion == "doblar":
            if len(monedas)>=apuestc:
                monedas=monedas[apuestc:]
                apuestc*=2
            else:
                await bot.say("No puedes doblar porque no tienes suficientes fichas",delete_after=6.0)
            await bot.edit_message(info,"**Fichas: %i**\n**Tiempo de cada ficha: %.2f (horas)**" % (
                len(monedas),nmoneda.consultarExpiracion()/60/60
            ))
            jugador = j.bjpedir(jugador,rp)
            playercards=", ".join([card.split(" ")[1] for card in jugador["cartas"]])
            playervalor=j.bjvalor(jugador)
            playercards = "{%s (%i)}" % (playercards,playervalor)
            opc = playercards.join(re.split(r"\{[^\}]+\}",opc))
            await bot.edit_message(ronda,opc+"\n```")
            if playervalor>21:
                ploses=True
        elif opcion == "dividir" and dividir:
            pass
        elif opcion == "777" and _777:
            if len(monedas)>=apuestc*2:
                monedas=monedas[apuestc*2:]
                await bot.edit_message(info,"**Fichas: %i**\n**Tiempo de cada ficha: %.2f (horas)**" % (
                    len(monedas),monedas[0].consultarExpiracion()/60/60
                ))
                jugador = j.bjpedir(jugador,rp)
                playercards=", ".join([card.split(" ")[1] for card in jugador["cartas"]])
                playervalor=j.bjvalor(jugador)
                playercards = "{%s (%i)}" % (playercards,playervalor)
                await bot.edit_message(ronda,playercards.join(re.split(r"\{[^\}]+\}",opc))+"\n```")
                if all([c[0]=="7" for c in jugador["cartas"]]):
                    monedas+=[banco.ClonarMoneda(nmoneda) for _ in range(apuestc*10)]
                    await bot.edit_message(info,"**Fichas: %i**\n**Tiempo de cada ficha: %.2f (horas)**" % (
                        len(monedas),nmoneda.consultarExpiracion()/60/60
                    ))
                elif playervalor>21:
                    ploses=True
            else:
                await bot.say("No puedes hacer esta apuesta porque no tienes suficientes fichas",delete_after=6.0)
        elif opcion == "pedir":
            while True:
                jugador=j.bjpedir(jugador,rp)
                playercards=", ".join([card.split(" ")[1] for card in jugador["cartas"]])
                playervalor=j.bjvalor(jugador)
                playercards = "{%s (%i)}" % (playercards,playervalor)
                opc = playercards.join(re.split(r"\{[^\}]+\}",opc))
                await bot.edit_message(ronda,opc+"\n```")
                if playervalor==21:
                    break
                elif playervalor>21:
                    ploses=True
                    break
                else:
                    await bot.say("Quieres pedir otra carta? (si/no)",delete_after=4.0)
                    pedir = await bot.wait_for_message(channel=canal,author=ctx.message.author,timeout=4)
                    if pedir:
                        await bot.delete_message(pedir)
                        if pedir.content.lower()=="no":
                            break
                    else:
                        break
        else:
            await bot.say("Opcion no valida, mantener por defecto",delete_after=2.0)
        if ploses:
            await bot.say("Perdiste",delete_after=2.0)
            continue
        while True:
            await asyncio.sleep(1.5)
            dealercards=", ".join([card.split(" ")[1] for card in dealer["cartas"]])
            dealervalor=j.bjvalor(dealer)
            dealercards = "[%s (%i)]" % (dealercards,dealervalor)
            opc = dealercards.join(re.split(r"\[[^\]]+\]",opc))
            await bot.edit_message(ronda,opc+"\n```")
            if dealervalor<=16:
                dealer=j.bjpedir(dealer,rp)
            else:
                break
        pv,dv=j.bjvalor(jugador),dealervalor
        if dv>21 or pv>dv:
            await bot.say("Ganaste",delete_after=2.0)
            if pv==21:
                monedas+=[banco.ClonarMoneda(nmoneda) for _ in range(apuestc*3)]
            else:
                monedas+=[banco.ClonarMoneda(nmoneda) for _ in range(apuestc*2)]
        elif dv==pv:
            await bot.say("Empate",delete_after=2.0)
            monedas+=[banco.ClonarMoneda(nmoneda) for _ in range(apuestc)]
        elif dv>pv:
            await bot.say("Perdiste",delete_after=2.0)
        await bot.edit_message(info,"**Fichas: %i**\n**Tiempo de cada ficha: %.2f (horas)**" % (
            len(monedas),nmoneda.consultarExpiracion()/60/60
        ))
    await bot.delete_message(info)
    await bot.delete_message(ronda)
    fichas=j.regresarFichas(len(monedas))
    c.eliminarMoneda(moneda.getID())
    banco.deleteID(moneda.getID(),dbt)
    print(fichas)
    await bot.say(ctx.message.author.mention+"   **Recompensa obtenida:**")
    for f in fichas:
        nmoneda=banco.TMoneda(f,moneda.consultarExpiracion(),banco.makeID(dbt))
        c.agregarMoneda(nmoneda)
        m=nmoneda.__json__()
        s=segundosV(m["expiracion"])
        await bot.say("\n```\n%s:{\n\tduracion: %i dias,%i horas,%i minutos\n\tvalor: %i\n}```" % (
            hex(m["ID"])[2:].upper(),
            s["dias"],
            s["horas"],
            s["minutos"],
            m["valor"]
            )
        )
    c.actualizarSaldo()

@bot.command(pass_context=True)
async def texasholdem(ctx):
    canal = ctx.message.channel
    if canal.type=="private":
        await bot.say("Solo puedes empezar una partida en un canal publico")
        return

#Luis Albizo 13/01/18
