from bs4 import BeautifulSoup as bs
import requests as r
import urllib as ul

def get_meta_info(what,soup):
    try:
        return soup.find("meta",{"name":what})["content"]
    except:
        return str()

def get_ext(url):
    return url[-4:]

def fix_rel(url,prot="http"):
    if url[:len(prot)]==prot:
        return url
    else:
        if url[:2]=="//":
            return prot+":"+url
        else:
            return prot+":/"+url


main_chan="http://www.4chan.org/"
Board="http://boards.4chan.org"
actual_url=None

def get_tab(url):
    return url[url.index("g")+1:]

def get_thread_files(url):
    fsp=bs(r.get(url).content,"html.parser")
    files=fsp.findAll("div",{"class":"fileText"})
    for el in files:
        current_file=el.find("a")
        yield "http:"+current_file["href"]

def main_screen():
    sp=bs(r.get(main_chan).content,"html.parser")
    tablones=sp.findAll("div",{"class":"boxcontent"})[1]
    temas=tablones.findAll("h3",{"style":"text-decoration: underline; display: inline;"})
    temtabs=tablones.findAll("ul")
    tabs=dict()
    screen = "```"
    screen+="\n\t\tStats\n"
    for el in sp.findAll("div",{"class":"stat-cell"}):
        screen+=(el.text+"\n")
    screen+= "\n\t\tBoards\n"
    for el in range(0,len(temas)):
        screen+=(temas[el].text+"\n")
        for ele in temtabs[el].findAll("li"):
            screen+=("\t"+ele.text+" - "+get_tab(ele.find("a")["href"])+"\n")
    return screen+"```"
        
def get_threads(board_page):
    global actual_url
    threads={}
    soup=bs(r.get(board_page).content, "html.parser")
    board=actual_url
    if board[-2] in "0123456789":
        board = board[:-2]
    tdb=soup.findAll("div",{"class":"thread"})
    i=1
    for el in tdb:
        op=el.find("div",{"class":"postContainer opContainer"})
        post_info=op.find("span",{"class":"name"}).text+" "+op.find("span",{"class":"dateTime postNum"}).text
        postid=op.find("a",{"title":"Reply to this post"})
        try:
            file_info=op.find("div",{"class":"fileText"})
            file_url=fix_rel(file_info.find("a")["href"])
            file_info=file_info.text
        except:
            file_info=str()
            file_url=str()
        replys=str(op.find("span",{"class":"info"}).text)
        title_thread=str(op.find("span",{"class":"subject"}).text)
        message=str(op.find("blockquote",{"class":"postMessage"}).text)
        threads[i]={"post_id":postid,"post_info":post_info,"post_url":board+postid["href"].split("#")[0]}
        threads[i]["file_info"]=file_info
        threads[i]["file_url"]=file_url
        threads[i]["title"]=title_thread
        threads[i]["message"]=message
        threads[i]["replys"]=replys
        i+=1
    return threads

def display_board(threads):
    for k in range(1,len(threads)+1):
        b="```"
        t=threads[k]
        b+="\n\t[idshort]:"+str(k)
        b+=("\nTitle: "+t["title"]+"\n"+"Info: "+t["post_info"])
        b+=("\n"+t["file_info"])
        b+=("\nMessage:\n"+t["message"]+"\n"+t["replys"]+"\n")
        yield b+"```"


def goto_board(board):
    global Board
    global actual_url
    mm="```\nYour request: "+board+" "
    actual_url=Board+board
    req = r.get(actual_url)
    sp=bs(req.content, "html.parser")
    mm+=(sp.find("title").text+"\n"+get_meta_info("description",sp))
    if req.status_code>400:
        return {"error":True,"content":(mm+("\nOops. 404, try again :(```"))}
    else:
        threads=get_threads(actual_url)
        return {"error":False , "content":[mm+"```",display_board(threads),
            "**Type an idshort to view all images of that thread**"],
            #"```\n\tOptions:\n[i] : download by id\n[m] : go to main\n[c] : change current page\n[x] : exit```"]
            "threads":threads
            }

"""
    opc=input("option: ")
    if opc=="i":
        idshort=int(input("select idshort: "))
        self.get_thread_files(threads[idshort]["post_url"],input("directory: ")+"/")
    elif opc=="m":
        self.main_screen()
    elif opc=="c":
        page=input("Enter number of page: ")
        self.goto_board(self.actualboard+page)
"""

#Luis Albizo 10/10/16
