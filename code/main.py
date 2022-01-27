import sys
import json
import requests
import pandas as pd

lat = input("Latitude of area: ")
while float(lat) < -90.0 and float(lat) > 90.0 :
    print("Invalid range for latitude...")
    lat = input("Please give valid input (-90, 90): ")

lon = input("Longitude of area: ")
while float(lon) < -180.0 and float(lon) > 180.0 :
    print("Invalid range for longitude...")
    lat = input("Please give valid input (-180, 180): ")

solar = float(input("Grid-connected solar power (kWp): "))
while solar <= 0:
    print("Installed kWp cannot be below zero...")
    solar = input("Please give valid input: ")

url = "https://re.jrc.ec.europa.eu/api/PVcalc?lat="+lat+"&lon="+lon+"&peakpower=1&loss=14&outputformat=json"
r = requests.get(url)

if r.status_code == 200:
    df = pd.json_normalize(r.json()['outputs']['monthly']['fixed'])

    average_solarenergy_peryear = df['E_m'].sum()
    solarenergy_produced_peryear = average_solarenergy_peryear * solar

    print('{} kWh/year produced by solar panels'.format(solarenergy_produced_peryear))

elif r.status_code == 400:
    sys.exit(r.json()['message'])

with open('/home/manousos/myfiles/thesis/data/battery.json', 'r') as f:
    bat = json.load(f)

    bat_energy_percycle = bat['voltage'] * bat['capacity'] * bat['dod']
    bat_energy_perlifetime = bat_energy_percycle * bat['cycles']
    print("Battery can store {} kWh in it's lifetime".format(bat_energy_perlifetime))
