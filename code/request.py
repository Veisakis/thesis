import os
import sys
import json
import requests
import pandas as pd

from prompt import path, lat, lon, solar

startyear = "2014"
endyear = "2014"
loss = "14"
angle = lat

url = ("https://re.jrc.ec.europa.eu/api/seriescalc?lat="
     +lat+"&lon="+lon+"&startyear="+startyear+"&endyear="
     +endyear+"&peakpower="+str(solar)+"&angle="+angle
     +"&loss="+loss+"&pvcalculation=1")
r = requests.get(url)

if r.status_code == 300:
    print("\nConnection Established!\nDownloading data...\n")

    os.system("curl \'" + url + "\' | tail -n +11 | head -n -11 > " + path + "/data/pv_formatted.csv")
    print("\nSaved data to file pv_formatted.csv")

else:
    sys.exit("\nConnection failed\nStatus Code: " + str(r.status_code))
