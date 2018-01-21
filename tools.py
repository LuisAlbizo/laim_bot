import random,time,subprocess
abc="abcdefghijklmnopqrstuvwxyz"
abc=abc+abc.upper()+"_0123456789"

def joinToStr(lista,sep=""):
	strGen=""
	for element in lista:
		strGen=strGen+element+sep
	return strGen[:-len(sep)]

def localtime():
		timestamp=time.localtime()
		day,month,year=timestamp.tm_mday,timestamp.tm_mon,timestamp.tm_year
		hour,minu,sec=timestamp.tm_hour,timestamp.tm_min,timestamp.tm_sec
		timestamp="%i-%i-%i %i:%i:%i" % (year,month,day,hour,minu,sec)
		return timestamp

def lsl(route):
	lslBruto=subprocess.check_output(("ls -l %s/" % joinToStr(route.split(" "),"\\ ")),shell=True).decode().split("\n")
	lslI=[]
	listdir=[]
	lsAux=[]
	for el in lslBruto:
		lsAux.append(el.split(" "))
	for el in lsAux:
		elem=[]
		for ele in el:
			if ele!="":
				elem.append(ele)
		listdir.append(elem)
	for el in listdir:
		elI={}
		if len(el)==0:
			pass
		elif el[0][0]=="d":
			elI["type"]="dir"
			elI["date"]=el[4]+" "+el[3]
			elI["name"]=joinToStr(el[5:]," ")
			lslI.append(elI)
		elif el[0][0]=="-":
			elI["type"]="file"
			elI["size"]=int(el[3])
			elI["date"]=el[5]+" "+el[4]
			elI["name"]=joinToStr(el[6:]," ")
			lslI.append(elI)
		else:
			pass
	return lslI

def randomString(lenght=10):
	global abc
	strGen=""
	for _ in range(lenght):
		strGen+=abc[random.randint(0,len(abc)-1)]
	return strGen

