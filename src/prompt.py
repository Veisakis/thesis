import os
import sys
import json
import math
import requests
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


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

print("Choose storage method:")
method = int(input("[1] Store all energy produced\n"
                   + "[2] Store only excess energy\n"))
                   
while method > 2 or method < 1:
    print("\nInvalid answer. Please choose one of the below:")
    method = int(input("[1] Store all energy produced\n"
                       + "[2] Store only excess energy\n"))
                       
print("\nSelect pre-defined place from the list below (1-5)")
print("or press 6 to provide custom coordinates:\n")

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


solar = int(input("\nTotal installed solar power in the area (Wp): "))
while solar <= 0:
    print("Installed Wp cannot be below zero...")
    solar = int(input("Please provide valid input (Wp): "))
