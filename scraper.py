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
        yield current_file["href"]

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
    soup=bs(r.get(board_page).content)
    board=actual_url
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
    b="```"
    for k in range(1,len(threads)+1):
        t=threads[k]
        b+="\t[idshort]:"+str(k)
        b+=("Title: "+t["title"]+"\n"+"Info: "+t["post_info"])
        b+=(t["file_info"])
        b+=("Message:\n"+t["message"]+"\n"+t["replys"]+"\n")
    return b+"```"


def goto_board(board):
    mm="```\nYour request: "+board
    actual_url=Board+board
    sp=bs(r.get(self.__actual_url).content,"html.parser")
    mm+=(sp.find("title").text+"\n"+get_meta_info("description",sp))
    if sp.find("title").text[:3]=="404":
        return mm+("\n404 - back to main```")
    threads=self.get_threads(self.__actual_url)
    self.display_board(threads)
    mm+=("\n\tOptions:\n[i:download by idshort]\n[m:go to main]\n[c:change current page]\n[_x:exit]```")


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
