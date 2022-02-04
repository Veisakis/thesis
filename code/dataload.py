import os
import sys
import json
import requests
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from prompt import path, lat, lon, solar

startyear = "2014"
endyear = "2014"
loss = "14"
angle = lat

url = ("https://re.jrc.ec.europa.eu/api/seriescalc?lat="
     +lat+"&lon="+lon+"&startyear="+startyear+"&endyear="
     +endyear+"&peakpower="+str(solar)+"&angle="+angle
     +"&loss="+loss+"&pvcalculation=1")
r = requests.get(url)

if r.status_code == 300:
    print("\nConnection Established!\nDownloading data...\n")

    os.system("curl \'" + url + "\' | tail -n +11 | head -n -11 > " + path + "/data/pv_formatted.csv")
    print("\nSaved data to file pv_formatted.csv")

else:
    sys.exit("\nConnection failed\nStatus Code: " + str(r.status_code))



gridload = pd.read_csv(path + "/data/moires_gridload.csv", sep=":")
pv = pd.read_csv(path + "/data/pv_formatted.csv")

y_grid = gridload.drop(gridload.columns[0:2], axis=1).stack().array
y_pv = pv['P'].array / 1_000_000 # converting to MW from W
x = range(8760)

plt.plot(x, y_grid)
plt.plot(x, y_pv)
plt.show()


balance = np.array(y_pv - y_grid)
positive_energy_sum = balance[balance > 0].sum()
positive_energy_hours = balance[balance > 0].size
excess_energy = positive_energy_sum * positive_energy_hours

print(f'\n{excess_energy:.3} MWh are wasted!')
