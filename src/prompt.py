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
    bat_type = path + "/data/lead_carbon.json"
else:
    bat_type = path + "/data/lithium_ion.json"

cost = int(input("\nSet cost limit (if none, enter 0): "))
while cost < 0:
    print("\nInvalid answer!")
    cost = int(input("Set cost limit (if none, enter 0): "))

print("\nSelect examination area from the list below (1-5)")
place = int(input("[1] Chania\n[2] Rethymno\n"
                  + "[3] Heraklio\n[4] Ag.Nikolaos\n[5] Moires\n"))

while place > 6 or place < 1:
    print("\nInvalid answer. Please choose one of the below:")
    place = int(input("[1] Chania\n[2] Rethymno\n"
                      + "[3] Heraklio\n[4] Ag.Nikolaos\n[5] Moires\n"))

lat = str(places[place][0])
lon = str(places[place][1])

solar = int(input("\nHow much solar is to be placed in the area (kWp)? "))
while solar <= 0:
    print("Installed kWp cannot be below zero...")
    solar = int(input("Please provide valid input (kWp): "))