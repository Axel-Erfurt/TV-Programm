#!/usr/bin/python3
# -*- coding: utf-8 -*-
import requests
import time
import sys
from subprocess import call
url = "http://mobile.hoerzu.de/programbystation"
chList = ["ard","zdf","arte","zdf neo","zdf info","wdr","ndr","mdr","hr","swr","br",\
            "rbb","3sat","kika","phoenix","tagesschau","one", "rtl", "sat 1", "pro 7", "kabel 1", \
            "rtl 2", "vox", "rtl nitro", "n24 doku", "kabel 1 doku", "sport 1", "super rtl", \
            "sat 1 gold", "vox up", "sixx", "servus tv", "super rtl"]       
 
idList = [71,37,58,659,276,46,47,48,49,10142,51,52,56,57,194,100,146,38,39,\
          40,44,41,42,763,12045,12043,64,12033,774,12125,694,660,43]

ergebnisliste = []
r = requests.get(url)
  
### to json 
data = r.json() 


def getValues(channel):
    theList = []
    for i in data:
        if i['id'] == channel:
            pr = i['broadcasts']
            for a in pr:
                title = str(a.get('title'))
                st = a.get('startTime')
                start = time.strftime("%H:%M", time.localtime(st))
                
                theList.append(f"{start} Uhr: {title}")
    return theList

for x in range(len(idList)):
    ergebnisliste.append(chList[x].upper())
    ergebnisliste.append('#########################')
    p = getValues(idList[x]) 
    ergebnisliste.append('\n'.join(p))
    ergebnisliste.append('#########################')
print('\n'.join(ergebnisliste))
    
if len(sys.argv) > 1:
    outfile = sys.argv[1]
else:
   outfile = "/tmp/programm.txt"
   
with open(outfile, 'w') as f:
    f.write('\n'.join(ergebnisliste))
    f.close()
    
call(('xdg-open', outfile))