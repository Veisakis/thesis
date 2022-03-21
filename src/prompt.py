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