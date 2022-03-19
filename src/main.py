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
timespan = range(8760)

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

print("\nChoose battery type:")
type = int(input("[1] Lead-Carbon\n"
                 + "[2] Lithium-Ion\n"))

while type > 2 or type < 1:
    print("\nInvalid answer. Please choose one of the below:")
    type = int(input("[1] Lead-Carbon\n"
                     + "[2] Lithium-Ion\n"))

if type == 1:
    bat_type = path + "/data/lead_carbon.json"
else:
    bat_type = path + "/data/lithium_ion.json"

print("\nGive a search range for the number of batteries:")
min = int(input("Min: "))
max = int(input("Max: "))

while min < 1:
    print("\nBatteries must be more than or equal to 1.")
    min = int(input("Min: "))

while max < min:
    print("\nMax must be greater than min.")
    max = int(input("Max: "))
    
print("\nSelect pre-defined place from the list below (1-5)")
print("or press 6 to provide custom coordinates:")

place = int(input("[1] Chania\n[2] Rethymno\n"
                  + "[3] Heraklio\n[4] Ag.Nikolaos\n"
                  + "[5] Moires\n[6] Custom\n"))

while place > 6 or place < 1:
    print("\nInvalid answer. Please choose one of the below:")
    place = int(input("[1] Chania\n[2] Rethymno\n"
                      + "[3] Heraklio\n[4] Ag.Nikolaos\n"
                      + "[5] Moires\n[6] Custom\n"))

if place == 6:
    lat = input("Latitude of area: ")
    while float(lat) < -90.0 or float(lat) > 90.0:
        print("Invalid range for latitude...")
        lat = input("Please provide valid input (-90, 90): ")

    lon = input("Longitude of area: ")
    while float(lon) < -180.0 or float(lon) > 180.0:
        print("Invalid range for longitude...")
        lat = input("Please provide valid input (-180, 180): ")
else:
    lat = str(places[place][0])
    lon = str(places[place][1])

solar = int(input("\nTotal installed solar power in the area (kWp): "))
while solar <= 0:
    print("Installed kWp cannot be below zero...")
    solar = int(input("Please provide valid input (kWp): "))


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
       + endyear+"&peakpower="+str(solar)+"&angle="+angle
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
    bat = Battery.from_json(bat_type)
except Exception as err:
    print("\nFailed to instantiate battery object from json file...\n")
    sys.exit(err)

'''Optimization'''
pv, gridload, gridload_mean = processData.formatData(pv_raw, gridload_raw)
pv, gridload, gridload_flattened, bat = processData.batteryOptimization(pv, gridload, 
                                                                        gridload_mean, min, max, bat)

print(f'\n{"Optimization Results":-^65}')
print(f'Batteries: {bat.number}')
print(f'Total Cost: {format(bat.cost, ",")}€\n')
'''Optimization'''

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
ax2.axhline(y=gridload_mean, color="red",
            linestyle='--', alpha=0.50,
            label='Gridload Mean Value')

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