import requests
import pandas as pd

try:
    gridload_raw = pd.read_csv(path + "/data/moires_gridload.csv", sep=":")
except FileNotFoundError:
    print("File not found!\nExiting...")
    sys.exit()
else:
    print("\nLoaded gridload data for the area.")


print("Fetching PV data from PV-GIS...\n")
url = ("https://re.jrc.ec.europa.eu/api/seriescalc?lat="
       + lat+"&lon="+lon+"&startyear="+startyear+"&endyear="
       + endyear+"&peakpower="+str(solar/1000)+"&angle="+angle
       + "&loss="+loss+"&pvcalculation=1")

try:
    r = requests.get(url)
except ConnectionError:
    print("Couldn't connect to PV-GIS!\nExiting...")
    print(f'Status code: {r.status_code}')
    sys.exit()
else:
    print("\nConnection Established!\n")
    os.system("curl \'"+url+"\' | tail -n+11 | head -n-11 >"+path+"/data/pv_production.csv")
    print("\nSaved data to file pv_production.csv")


try:
    pv_raw = pd.read_csv(path + "/data/pv_production.csv")
except FileNotFoundError as err:
    sys.exit(err)


try:
    bat = Battery.from_json("/home/manousos/myfiles/thesis/data/lead_carbon.json")
except Exception as err:
    print("Failed to instantiate battery object from json file...")
    sys.exit(err)

