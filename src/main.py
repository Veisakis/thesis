import os
import sys
import json
import math
import requests
import numpy as np
import pandas as pd

from matplotlib import pyplot as plt
from requests.exceptions import ConnectionError

import processData, economics
from battery import Battery

min = 1
max = 100
timespan = range(500, 800)

loss = "14"
angle = "30"
endyear = "2014"
startyear = "2014"

pv_cost_perkW = 1_000
discount_rate = 0.06
project_lifetime = 25

path = os.environ['HOME']

places = {
    1: (35.512, 24.012),
    2: (35.364, 24.471),
    3: (35.343, 25.153),
    4: (35.185, 25.706),
    5: (35.050, 24.877)
}

os.system("clear")
os.system("figlet TEI Crete")
print("'How many batteries need to be installed, to handle more renewables on the grid?'\n"
      + "An optimization script to solve this problem.\n"
      + "\nOptimization ends when either:\n"
      + "(1) No more renewable energy produced, is wasted.\n"
      + "(2) Renewables and batteries can supply 100% of gridload.\n"
      + "(3) Cost limit is reached (if set).\n")

print("\nChoose battery type:")
type = int(input("[1] Lead-Carbon (300,000.00€/MWh)\n"
                 + "[2] Lithium-Ion (500,000.00€/MWh)\n"))

while type > 2 or type < 1:
    print("\nInvalid answer. Please choose one of the below:")
    type = int(input("[1] Lead-Carbon\n"
                     + "[2] Lithium-Ion\n"))

if type == 1:
    bat_type = path + "/thesis/data/lead_carbon.json"
else:
    bat_type = path + "/thesis/data/lithium_ion.json"

cost = int(input("\nSet cost limit (if none, enter 0): "))
while cost < 0:
    print("\nInvalid answer!")
    cost = int(input("Set cost limit (if none, enter 0): "))

print("\nSelect examination area from the list below (1-5)")
place = int(input("[1] Chania\n[2] Rethymno\n"
                  + "[3] Heraklio\n[4] Ag.Nikolaos\n[5] Moires\n"))

while place > 5 or place < 1:
    print("\nInvalid answer. Please choose one of the below:")
    place = int(input("[1] Chania\n[2] Rethymno\n"
                      + "[3] Heraklio\n[4] Ag.Nikolaos\n[5] Moires\n"))

lat = str(places[place][0])
lon = str(places[place][1])

solar = int(input("\nHow much solar is to be placed in the area (kWp)? "))
while solar <= 0:
    print("Installed kWp cannot be below zero...")
    solar = int(input("Please provide valid input (kWp): "))


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

'''Optimization'''
pv, gridload, gridload_mean = processData.formatData(pv_raw, gridload_raw)
pv, gridload, wasted_energy, gridload_aided, gridload_flattened, gridload_mean, bat, found = processData.batteryOptimization(pv, gridload, gridload_mean,
                                                                                                                             min, max, bat_type, cost)
solar_cost = format(round(solar*pv_cost_perkW, 2), ",")
bat_cost = format(round(bat.cost, 2), ",")
total_cost = format(round(bat.cost+solar*pv_cost_perkW, 2), ",")

print(f'\n{"Optimization Results":-^65}')
print(f'PV: {solar} kWp')
print(f'Batteries: {bat.number}\n')
print(f'PV Installation Cost: {solar_cost} €')
print(f'Batteries Cost: {bat_cost} €')
print(f'Total Cost: {total_cost} €')
print(f'{"Notes":-^65}')

if found == 1:
    print("Cost limit has been reached.")
elif found == 2:
    print("The gridload curve has been stabilized.\n"
          + "No excess energy, produced by renewables, is wasted.\n"
          + "No need for more than {number} batteries.".format(number=bat.number))
elif found == 3:
    print("Renewables supply the grid at 100%!")

print(f'{"!":-^65}\n')
'''Optimization'''

'''Plot'''
plt.style.use('classic')
fig, (ax1, ax2) = plt.subplots(nrows=2, ncols=1)

ax1.plot(timespan, pv[timespan], linestyle='dashed',
         color='darkolivegreen', label='PV power output')
ax1.plot(timespan, gridload[timespan],
         color='saddlebrown', label='Grid Load')

ax1.fill_between(timespan, pv[timespan], gridload[timespan],
                 where=(pv[timespan] > gridload[timespan]), interpolate=True,
                 color='yellowgreen', alpha=0.40, label='Excess Energy')

ax1.set_xticks(timespan)
ax1.set_xlim(timespan[0], timespan[-1])

ax1.set_ylabel('Power (W)')
ax1.set_title('Grid load and PV power output curves')

ax1.grid(True)
ax1.legend(loc='upper left')


ax2.plot(timespan, gridload_aided[timespan],
         color='saddlebrown', label='Grid Load without battery storage')
ax2.plot(timespan, gridload_flattened[timespan],
         color='darkolivegreen', label='Grid Load with battery storage')

ax2.fill_between(timespan, gridload[timespan], color='saddlebrown', alpha=0.50)
ax2.fill_between(timespan, gridload_flattened[timespan], color='olive', alpha=0.30)

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
