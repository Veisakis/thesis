import os
import sys
import json
import math
import requests
import numpy as np
import pandas as pd

from matplotlib import pyplot as plt
from requests.exceptions import ConnectionError

import processData
from battery import Battery


loss = "14"
angle = "30"
endyear = "2014"
startyear = "2014"
timespan = range(24)

path = "/home/manousos/myfiles/thesis"

places = {
    1: (35.512, 24.012),
    2: (35.364, 24.471),
    3: (35.343, 25.153),
    4: (35.185, 25.706),
    5: (35.050, 24.877)
}

os.system("clear")
os.system("figlet TEI Crete")
print("Select pre-defined place from the list below (1-5)")
print("or press 6 to provide custom coordinates:\n")

choice = int(input("[1] Chania\n[2] Rethymno\n"
                   + "[3] Heraklio\n[4] Ag.Nikolaos\n"
                   + "[5] Moires\n[6] Custom\n"))

while choice > 6 or choice < 1:
    print("\nInvalid answer. Please choose one of the below:")
    choice = int(input("[1] Chania\n[2] Rethymno\n"
                       + "[3] Heraklio\n[4] Ag.Nikolaos\n"
                       + "[5] Moires\n[6] Custom\n"))


if choice == 6:
    lat = input("Latitude of area: ")
    while float(lat) < -90.0 or float(lat) > 90.0:
        print("Invalid range for latitude...")
        lat = input("Please provide valid input (-90, 90): ")

    lon = input("Longitude of area: ")
    while float(lon) < -180.0 or float(lon) > 180.0:
        print("Invalid range for longitude...")
        lat = input("Please provide valid input (-180, 180): ")
else:
    lat = str(places[choice][0])
    lon = str(places[choice][1])


solar = int(input("\nTotal installed solar power in the area (Wp): "))
while solar <= 0:
    print("Installed Wp cannot be below zero...")
    solar = int(input("Please provide valid input (Wp): "))


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
    print("\nSaved data to file pv_production.csv\n")

try:
    pv_raw = pd.read_csv(path + "/data/pv_production.csv")
except FileNotFoundError as err:
    sys.exit(err)

try:
    bat = Battery.from_json("/home/manousos/myfiles/thesis/data/lead_carbon.json")
except Exception as err:
    print("\nFailed to instantiate battery object from json file...\n")
    sys.exit(err)


pv, gridload = processData.formatData(pv_raw, gridload_raw)

solar_energy = processData.solarProduction(pv)
target_energy = processData.targetEnergy(gridload)

solar_batteries = bat.batteriesNeeded(solar_energy)
target_batteries = bat.batteriesNeeded(target_energy)

print(f'Daily Solar Production (Wh){solar_energy:.>60.2f}')
print(f'Batteries Required to Store this energy{solar_batteries:.>48}\n')

print(f'Energy Required to flatten the Curve (Wh){target_energy:.>46.2f}')
print(f'Batteries Required to Store this energy{target_batteries:.>48}\n')

minimum_batteries, optimizedBatteryPack, gridload_flattened = processData.batteriesOptimize(target_batteries,
                                                                                            solar_batteries, gridload)

print(f'\n{"Optimization Results":-^65}')
print(f'Batteries: {minimum_batteries}')
print(f'State of Charge (after grid stabilization): {optimizedBatteryPack.stateOfCharge() * 100:.2f}%')
print(f'Total Cost: {format(optimizedBatteryPack.cost * minimum_batteries, ",")}€\n')

'''Plot'''
plt.style.use('classic')
fig, (ax1, ax2) = plt.subplots(nrows=2, ncols=1)

ax1.plot(timespan, pv, linestyle='dashed',
         color='darkolivegreen', label='PV power output')
ax1.plot(timespan, gridload,
         color='saddlebrown', label='Grid Load')

ax1.fill_between(timespan, pv, gridload,
                 where=(pv > gridload), interpolate=True,
                 color='yellowgreen', alpha=0.40, label='Excess Energy')

ax1.set_xticks(timespan)
ax1.set_xlim(timespan[0], timespan[-1])

ax1.set_ylabel('Power (W)')
ax1.set_title('Grid load and PV power output curves')

ax1.grid(True)
ax1.legend(loc='upper left')


ax2.plot(timespan, gridload,
         color='saddlebrown', label='Grid Load without battery storage')
ax2.plot(timespan, gridload_flattened,
         color='darkolivegreen', label='Grid Load with battery storage')

ax2.fill_between(timespan, gridload, color='saddlebrown', alpha=0.50)
ax2.fill_between(timespan, gridload_flattened, color='olive', alpha=0.30)

ax2.set_xticks(timespan)
ax2.set_xlim(timespan[0], timespan[-1])

ax2.set_xlabel('Hour of the day (h)')
ax2.set_ylabel('Power (W)')
ax2.set_title('Grid load "with" and "without" Batteries')

ax2.grid(True)
ax2.legend(loc='upper left')

plt.tight_layout()
plt.show()
'''Plot'''
