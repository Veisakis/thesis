import os
import requests
import pandas as pd

path = os.environ['HOME']

try:
    gridload_raw = pd.read_csv(path + "/thesis/data/moires_gridload.csv", sep=":")
except FileNotFoundError:
    print("File not found!\nExiting...")
    sys.exit()
else:
    print("\nLoaded gridload data for the area.")

print("\nFetching PV data from PV-GIS...")
url = ("https://re.jrc.ec.europa.eu/api/seriescalc?lat="
       + lat+"&lon="+lon+"&startyear="+startyear+"&endyear="
       + endyear+"&peakpower="+str(solar)+"&angle="+angle
       + "&loss="+loss+"&pvcalculation=1")

try:
    r = requests.get(url)
except ConnectionError:
    print("Couldn't connect to PV-GIS!\nExiting...")
    print(f'Status code: {r.status_code}')
    sys.exit()
else:
    print("Connection Established!\n")
    os.system("curl \'"+url+"\' | tail -n+11 | head -n-11 >"+path+"/thesis/data/pv_production.csv")
    print("\nSaved data to file pv_production.csv\n")

try:
    pv_raw = pd.read_csv(path + "/thesis/data/pv_production.csv")
except FileNotFoundError as err:
    sys.exit(err)

try:
    bat = Battery.from_json(bat_type)
except Exception as err:
    print("\nFailed to instantiate battery object from json file...\n")
    sys.exit(err)
