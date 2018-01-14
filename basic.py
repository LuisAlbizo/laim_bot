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

#Luis Albizo 09/10/16
