import os
import sys
import json
import requests
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

dur = 1
path = "/home/manousos/myfiles/thesis"
# startyear = "2014"
# endyear = "2014"
# loss = "14"
# angle = lat

# url = ("https://re.jrc.ec.europa.eu/api/seriescalc?lat="
#      +lat+"&lon="+lon+"&startyear="+startyear+"&endyear="
#      +endyear+"&peakpower="+str(solar)+"&angle="+angle
#      +"&loss="+loss+"&pvcalculation=1")
# r = requests.get(url)
#
# if r.status_code == 200:
#     print("\nConnection Established!\nDownloading data...\n")
#     os.system("curl \'"+url+"\' | tail -n+11 | head -n-11 >"+path+"/data/pv_formatted.csv")
#     print("\nSaved data to file pv_formatted.csv")
#
# else:
#     sys.exit("\nConnection failed\nStatus Code: " + str(r.status_code))



gridload = pd.read_csv(path + "/data/moires_gridload.csv", sep=":")
pv = pd.read_csv(path + "/data/pv_formatted.csv")

def year():
    global x, xlabel, y_grid, y_pv, period
    y_grid = gridload.drop(gridload.columns[0:2], axis=1).stack().array
    y_pv = pv['P'] / 1_000_000 # converting to MW from W

    x = range(8760)
    xlabel = 'Hour of the day'
    period = 'year'

def day():
    global x, xlabel, y_grid, y_pv, period
    y_grid = gridload.drop(gridload.columns[0:2], axis=1).mean()
    data_pv = pv['P'].iloc[::24] / 1_000_000 # converting to MW from W
    data_pv = data_pv.to_frame().rename(columns={'P': 0}).reset_index().drop(columns="index")

    for i in range(1,24):
        filter = pv['P'].iloc[i::24] / 1_000_000
        df_newcol = pd.DataFrame(filter)
        df_newcol = df_newcol.reset_index().drop(columns="index")
        data_pv[i] = df_newcol
    y_pv = data_pv.mean()

    x = range(24)
    xlabel = 'Hour of the day'
    period = 'day'

if dur == 1:
    day()
else:
    year()


plt.plot(x, y_grid)
plt.plot(x, y_pv)

plt.xlabel(xlabel)
plt.ylabel('Power (MW)')
plt.title('Grid load and Power output of PV')

plt.grid(True)
plt.legend(['Grid Load', 'PV output'])
plt.style.use('Solarize_Light2')

plt.show()


balance = np.array(y_pv.array - y_grid.array)
excess_power = balance[balance > 0].sum()
excess_power_duration = balance[balance > 0].size
excess_energy = excess_power * excess_power_duration

print(f'\n{excess_energy:.5} MWh are wasted each '+period+'!')


with open(path+"/data/battery.json", 'r') as f:
    data = json.load(f)
    bat = pd.DataFrame(data, index=[0])

capacity = bat['capacity'].values / 1000 # converting to MWh from kWh
batteries_needed = excess_energy // capacity
print(f'{int(batteries_needed[0])} batteries are needed to '
        +'store this excess energy.')
