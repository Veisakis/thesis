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

print("Select examination area from the list below (1-7)")
place = int(input("[1] Chania\n[2] Rethymno\n[3] Hrakleio\n"
                  + "[4] Ag.Nikolaos\n[5] Moires\n[6] Ierapetra\n[7] Shteia\n"))

while place > 7 or place < 1:
    print("\nInvalid answer. Please choose one of the below:")
    place = int(input("[1] Chania\n[2] Rethymno\n[3] Hrakleio\n"
                      + "[4] Ag.Nikolaos\n[5] Moires\n[6] Ierapetra\n[7] Shteia\n"))

lat = str(config.place_coordinates[place][0])
lon = str(config.place_coordinates[place][1])

placename_gridload = config.path + "/thesis/data/" + config.place_name[place] + "_gridload.csv"
placename_wind = config.path + "/thesis/data/" + config.place_name[place] + "_wind.csv"

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

solar = int(input("\nHow much PV power is wanted to be placed in the area (kWp)? "))
while solar < 0:
    print("Installed kWp cannot be below zero...")
    solar = int(input("Please provide valid input: "))

wind = int(input("How much wind turbine power is wanted to be placed in the area (MWp)? "))
while wind < 0:
    print("Installed MWp cannot be below zero...")
    wind = int(input("Please provide valid input: "))

cost = int(input('Set cost limit (€). Ιf none, type 0: '))
while cost < 0:
    print("\nInvalid answer!")
    cost = int(input('Set cost limit (€)'))

solar_cost = solar * config.pv_cost_perkWp
wind_cost = wind * config.wt_cost_perMWp
res_cost = solar_cost + wind_cost

'''Optimization'''
pv_raw = fetchData.pvgis(lat, lon, solar)
wd_raw = fetchData.from_csv(placename_wind) * wind
gridload_raw = fetchData.from_csv(placename_gridload)

pv = fetchData.from_pvgis(pv_raw)
wt = fetchData.from_raw(wd_raw)[0]
res = pv + wt

gridload, gridload_mean = fetchData.from_raw(gridload_raw)

(res, gridload,
 wasted_energy, gridload_aided,
 gridload_flattened, gridload_mean,
 bat, found, npv, onm, reinvest, costs) = processData.batteryOptimization(res, gridload, gridload_mean,
                                                                          config.batSearch_start, config.batSearch_end, 
                                                                          bat_type, res_cost, cost)

npv = economics.euro(npv)
onm = economics.euro(onm)
reinvest = economics.euro(reinvest)
solar_cost = economics.euro(solar_cost)
wind_cost = economics.euro(wind_cost)
bat_cost = economics.euro(bat.cost)
total_cost = economics.euro(costs)

lifetime = "System lifetime is considered "+ str(config.project_lifetime) + " years"
infiltration = format(processData.renewablesInfiltration(gridload, gridload_flattened), ".2%")
carbon = format(processData.carbonEmissions(gridload, gridload_flattened), ",.0f")

print(f'\n{"*Optimization Results*":^85}')
print(f'{lifetime:-^85}')
print(f'PV: {solar:,} kWp')
print(f'PV Initial Cost: {solar_cost}\n')
print(f'WT: {wind:,} MWp')
print(f'WT Initial Cost: {wind_cost}\n')
print(f'Batteries: {bat.number}')
print(f'Batteries Initial Cost: {bat_cost}\n')
print(f'Operational and Maintenance Costs: {onm}')
print(f'Reinvesting Costs during lifetime: {reinvest}\n')
print(f'Total Cost in Present Value: {total_cost}')
print(f'{"Notes":-^85}')

if found == 1:
    print("Cost limit has been reached!")
elif found == 2:
    print("No excess energy, produced by renewables, is wasted.")
elif found == 3:
    print("Renewables supply the grid at 100%!")

print(f'There is a {infiltration} infiltration of renewables in the grid.')
print(f'{carbon} tonnes of CO2 emissions are prevented, during projects lifetime.') 
print(f'{"!":-^85}\n')

print("Main modifiable parameters stored in config.py:\n"
      + "\t(1) Min and Max battery optimization search range\n"
        + "\t(2) Days of the year to be shown in the final plot\n"
        + "\t(3) Project Lifetime\n"
        + "\t(4) PV cost (€/kWp)\n"
        + "\t(5) Energy sell price (€/Wh)\n"
        + "\t(6) Discount rate\n"
        + "\t(7) Operational and Maintenance Costs (% of initial cost)\n"
        + "\t(8) Tonnes of CO2 emissions per Wh\n"
        + "Feel free to tailor the source code to your needs!\n")
'''Optimization'''
'''Plot'''
pv_series = fetchData.to_series(pv)
wt_series = fetchData.to_series(wt)

plt.style.use('classic')
plt.rcParams['font.family'] = 'serif'

fig, (ax1, ax2) = plt.subplots(nrows=2, ncols=1)


ax1.plot(config.timespan, pv_series[config.timespan],
         color='tomato', label='PV power output')
ax1.plot(config.timespan, wt_series[config.timespan],
         color='deepskyblue', label='WT power output')
ax1.plot(config.timespan, gridload[config.timespan],
         color='darkslategrey', label='Grid Load')

ax1.fill_between(config.timespan, pv_series[config.timespan], gridload[config.timespan],
                 where=(pv_series[config.timespan] > gridload[config.timespan]), interpolate=True,
                 color='seagreen', alpha=0.40, label='Excess Energy')

ax1.fill_between(config.timespan, wt_series[config.timespan], gridload[config.timespan],
                 where=(wt_series[config.timespan] > gridload[config.timespan]),
                 interpolate=True, color='seagreen', alpha=0.40)

ax1.set_xticks(config.timespan, minor=True)
ax1.set_xticks(np.arange(config.timespan[0], config.timespan[-1], 24))
ax1.set_xlim(config.timespan[0], config.timespan[-1])

ax1.set_ylabel('Power (W)', fontsize='medium')
ax1.set_title('Grid load and RES power output curves', fontsize='x-large')

ax1.grid(which='minor', alpha=0.5)
ax1.grid(which='major', alpha=1.0)
ax1.legend(loc='upper left', fontsize='x-small')


ax2.plot(config.timespan, gridload_aided[config.timespan],
         color='darkslategrey', label='Grid Load without battery storage')
ax2.plot(config.timespan, gridload_flattened[config.timespan],
         color='sienna', label='Grid Load with battery storage')

ax2.fill_between(config.timespan, gridload_aided[config.timespan], color='darkslategrey', alpha=0.30)
ax2.fill_between(config.timespan, gridload_flattened[config.timespan], color='darkorange', alpha=0.30)

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
