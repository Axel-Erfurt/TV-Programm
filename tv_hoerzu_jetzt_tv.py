#!/usr/bin/python3
# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
from subprocess import Popen, PIPE

def getList():
    chList = ["das erste","zdf","arte","zdfneo","zdfinfo","wdr","ndr","mdr","hr","swr","br",\
                "rbb","3sat","kika","phoenix","tagesschau24","one", "dw", "rtl", "sat.1", "prosieben", "kabel eins", \
            "rtl zwei", "vox", "rtl nitro", "n24 doku", "kabel 1 doku", "sport 1", "super rtl", \
            "sat.1 gold", "voxup", "sixx", "servus tv", "super rtl", "rtl plus", "nitro"]
    url = "https://www.hoerzu.de/text/tv-programm/jetzt.php"
    
    myfile = "/tmp/jetzt.html"

    cmd = ["wget", url, "-O", myfile]
    process = Popen(cmd, stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()


    with open(myfile, 'r') as f:
        data=f.read()
        
        
    soup = BeautifulSoup(data, features="lxml")
    out = soup.get_text('\n').replace("* \n", '').replace(" .\n", '').replace("* ", '').replace(" , ", ' - ')\
                            .replace("Uhr\n\n", 'Uhr\n').partition("Uhr")[2].partition("\nnach oben")[0]

    pList = out.splitlines()

    for x in reversed(range(len(pList))):
        if pList[x] == '':
            del pList[x]
        elif not pList[x].partition(" -")[0].lower() in chList:
            del pList[x]
        
    return(pList)
 
def do(): 
    p = getList()
    t = '\n'.join(p)
    return t
    