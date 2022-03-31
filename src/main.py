import os
import sys
import json
import math
import requests
import numpy as np
import pandas as pd

from matplotlib import pyplot as plt
from requests.exceptions import ConnectionError

import fetchData, processData, economics, config
from battery import Battery


os.system("clear")
os.system("figlet TEI Crete")
print("'How many batteries need to be installed, to handle more renewables on the grid?'\n"
      + "An optimization script to solve this problem.\n"
      + "\nOptimization ends when either:\n"
      + "(1) No more renewable energy produced, is wasted.\n"
      + "(2) Renewables and batteries can supply 100% of gridload.\n"
      + "(3) Cost limit is reached (if set).\n")

print("Select examination area from the list below (1-5)")
place = int(input("[1] Chania\n[2] Rethymno\n[3] Heraklio\n"
                  + "[4] Ag.Nikolaos\n[5] Moires\n"))

while place > 5 or place < 1:
    print("\nInvalid answer. Please choose one of the below:")
    place = int(input("[1] Chania\n[2] Rethymno\n[3] Heraklio\n"
                      + "[4] Ag.Nikolaos\n[5] Moires\n"))

lat = str(config.place_coordinates[place][0])
lon = str(config.place_coordinates[place][1])

print("\nChoose battery type:")
type = int(input("[1] Lead-Carbon (300,000.00€/MWh@5000cycles)\n"
                 + "[2] Lithium-Ion (500,000.00€/MWh@6000cycles)\n"))

while type > 2 or type < 1:
    print("\nInvalid answer. Please choose one of the below:")
    type = int(input("[1] Lead-Carbon\n"
                     + "[2] Lithium-Ion\n"))

if type == 1:
    bat_type = config.path + "/thesis/data/lead_carbon.json"
else:
    bat_type = config.path + "/thesis/data/lithium_ion.json"

try:
    bat = Battery.from_json(bat_type)
except Exception as err:
    print("Failed to instantiate battery object from json file...\n")
    sys.exit(err)

solar = int(input("\nHow much solar is wanted to be placed in the area (kWp)? "))
while solar <= 0:
    print("Installed kWp cannot be below zero...")
    solar = int(input("Please provide valid input: "))

cost = int(input('Set cost limit (€). Ιf none, type 0: '))
while cost < 0:
    print("\nInvalid answer!")
    cost = int(input('Set cost limit (€)'))
solar_cost = solar * config.pv_cost_perkWp
res_cost = solar_cost

'''Optimization'''
pv_raw = fetchData.pvgis(lat, lon, solar)
gridload_raw = fetchData.csv(config.place_name[place])
res, gridload, gridload_mean = fetchData.formatData(pv_raw, gridload_raw)

(res, gridload,
 wasted_energy, gridload_aided,
 gridload_flattened, gridload_mean,
 bat, found, npv, onm, reinvest, costs) = processData.batteryOptimization(res, gridload, gridload_mean,
                                                                          config.min, config.max, bat_type,
                                                                          res_cost, cost)

npv = economics.euro(npv)
onm = economics.euro(onm)
reinvest = economics.euro(reinvest)
solar_cost = economics.euro(solar_cost)
bat_cost = economics.euro(bat.cost)
total_cost = economics.euro(costs)


print(f'\n{"Optimization Results":-^65}')
print(f'PV: {solar:,} kWp')
print(f'PV Initial Cost: {solar_cost}\n')
print(f'Batteries: {bat.number}')
print(f'Batteries Initial Cost: {bat_cost}\n')
print(f'Operational and Maintenance Costs: {onm}')
print(f'Reinvesting Costs during lifetime: {reinvest}\n')
print(f'Total Cost in Present Value: {total_cost}')
print(f'{"Notes":-^65}')

print(f'System lifetime is considered {config.project_lifetime} years.')
if found == 1:
    print("Cost limit has been reached!")
elif found == 2:
    print("No excess energy, produced by renewables, is wasted.")
elif found == 3:
    print("Renewables supply the grid at 100%!")
    
print(f'{"!":-^65}\n')

print("Main modifiable parameters stored in config.py:\n"
      + "\t(1) Min and Max battery optimization search range\n"
        + "\t(2) Days of the year to be shown in the final plot\n"
        + "\t(3) Project Lifetime\n"
        + "\t(4) PV cost (€/kWp)\n"
        + "\t(5) Energy sell price (€/Wh)\n"
        + "\t(6) Discount rate\n"
        + "\t(7) Operational and Maintenance Costs (% of initial cost)\n"
        + "Feel free to tailor the source code to your needs!\n")
'''Optimization'''

'''Plot'''
plt.style.use('classic')
fig, (ax1, ax2) = plt.subplots(nrows=2, ncols=1)


ax1.plot(config.timespan, res[config.timespan], linestyle='dashed',
         color='darkolivegreen', label='PV power output')
ax1.plot(config.timespan, gridload[config.timespan],
         color='saddlebrown', label='Grid Load')

ax1.fill_between(config.timespan, res[config.timespan], gridload[config.timespan],
                 where=(res[config.timespan] > gridload[config.timespan]), interpolate=True,
                 color='yellowgreen', alpha=0.40, label='Excess Energy')

ax1.set_xticks(config.timespan, minor=True)
ax1.set_xticks(np.arange(config.timespan[0], config.timespan[-1], 24))
ax1.set_xlim(config.timespan[0], config.timespan[-1])

ax1.set_ylabel('Power (W)', fontsize='medium')
ax1.set_title('Grid load and PV power output curves', fontsize='x-large')

ax1.grid(which='minor', alpha=0.5)
ax1.grid(which='major', alpha=1.0)
ax1.legend(loc='upper left', fontsize='x-small')


ax2.plot(config.timespan, gridload_aided[config.timespan],
         color='saddlebrown', label='Grid Load without battery storage')
ax2.plot(config.timespan, gridload_flattened[config.timespan],
         color='darkolivegreen', label='Grid Load with battery storage')

ax2.fill_between(config.timespan, gridload_aided[config.timespan], color='saddlebrown', alpha=0.50)
ax2.fill_between(config.timespan, gridload_flattened[config.timespan], color='olive', alpha=0.30)

ax2.set_xticks(config.timespan, minor=True)
ax2.set_xticks(np.arange(config.timespan[0], config.timespan[-1], 24))
ax2.set_xlim(config.timespan[0], config.timespan[-1])

ax2.set_xlabel('Hour of the year (h)', fontsize='medium')
ax2.set_ylabel('Power (W)', fontsize='medium')
ax2.set_title('Grid load "with" and "without" Batteries', fontsize='x-large')

ax2.grid(which='minor', alpha=0.5)
ax2.grid(which='major', alpha=1.0)
ax2.legend(loc='upper left', fontsize='x-small')

plt.tight_layout()
plt.show()
'''Plot'''
