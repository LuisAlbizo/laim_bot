import requests as r
from bs4 import BeautifulSoup as bs
import re

main_chan = "https://www.hispachan.org"

def main_screen():
    sp=bs(r.get(main_chan).content,"html.parser")
    tablones=sp.findAll("a",rel="board")
    screen = "```\n"
    screen+=sp.find("title").text
    screen+= "\n\tTablones:\n"
    for el in tablones:
        if el.text:
            if el.text[0].isupper():
                screen+=("%s - %s\n" % (el.text, el["href"]))
    return screen+"```"

def get_threads(board_page):
    threads={}
    b=r.get(main_chan+board_page)
    sopa=bs(b.content, "html.parser")
    hilos=sopa.find_all("div",id=re.compile(r"thread\d+[a-z]{1,3}"))
    i=1
    compr=lambda x: x.text if x else str()
    for el in hilos:
        op=el
        post_info=op.find("span",{"class":"postername"}).text+" "+op.find("span",{"class":"timer"}).text
        postid=op.find("span",{"class":"responder"}).find("a")["href"]
        replys=compr(op.find("span",{"class":"omittedposts"}))
        title_thread=compr(op.find("span",{"class":"filetitle"}))
        message=op.find("blockquote").text
        threads[i]={"post_id":postid,"post_info":post_info,"post_url":postid}
        threads[i]["title"]=title_thread
        threads[i]["message"]="".join(filter(lambda s: bool(s),"\n".join(filter(lambda s: bool(s),message.split('\n'))).split('\r')))
        threads[i]["replys"]="\n"+" ".join(filter(lambda s: bool(s),replys.split('\n')))
        i+=1
    return threads

def goto_board(board):
    mm="```\nTablon solicitado: "+board+" "
    req = r.get(main_chan+board)
    sp=bs(req.content, "html.parser")
    if req.status_code>400:
        return {"error":True,"content":(mm+("\nVaya... 404, prueba de nuevo :^(```"))}
    else:
        threads=get_threads(board)
        return {"error":False , "content":[mm+"```",display_board(threads)],
            "threads":threads
            }

def display_board(threads):
    for k in range(1,len(threads)+1):
        b="```"
        t=threads[k]
        b+=("\nPost %i de %i\n" % (k,len(threads)))
        b+=("\nTitulo: "+t["title"]+"\n"+"Info: "+t["post_info"])
        b+=("\nMensaje:\n"+t["message"]+"\n"+t["replys"]+"\n")
        yield b+"```"

def get_thread_files(url):
    fsp=bs(r.get(url).content,"html.parser")
    imgs=fsp.find_all("span", "filesize")
    for el in imgs:
        yield el.find("a")["href"]

