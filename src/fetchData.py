import os
import sys
import requests
import numpy as np
import pandas as pd

import config


def from_csv(filename):
    '''Convert csv data to raw form'''
    try:
        raw_data = pd.read_csv(filename)
    except FileNotFoundError:
        print(f'File {filename} not found!')
        sys.exit()
    else:
        return raw_data
        
        
def pvgis(lat, lon, solar):
    '''Get hourly solar production data for a year from pv-gis' API'''
    if solar == 0:
        return pd.read_csv(config.path + "/thesis/data/pv_production_template.csv")

    print("\nConnecting to PV-GIS...")
    url = ("https://re.jrc.ec.europa.eu/api/seriescalc?lat="
           + lat+"&lon="+lon+"&startyear="+config.startyear+"&endyear="
           + config.endyear+"&peakpower="+str(solar)+"&angle="+config.angle
           + "&loss="+config.loss+"&pvcalculation=1")

    try:
        r = requests.get(url)
    except ConnectionError:
        print("Couldn't connect to PV-GIS!")
        print(f'Status code: {r.status_code}')
        sys.exit()
    else:
        print("Connection Established!")
        os.system("curl --progress-bar \'"+url+"\' | tail -n+11 | head -n-11 >" +
                  config.path+"/thesis/data/pv_production.csv")
        print("Saved solar data to file pv_production.csv")

    try:
        pv_raw = pd.read_csv(config.path + "/thesis/data/pv_production.csv")
    except FileNotFoundError as err:
        sys.exit(err)
    return pv_raw


def from_pvgis(pv_raw):
    '''Convert PV-GIS data to appropriate form'''
    pv = pv_raw['P'].iloc[::24]
    pv = pv.to_frame().rename(columns={'P': 0}).reset_index().drop(columns="index")
    for i in range(1, 24):
        filter = pv_raw['P'].iloc[i::24]
        df_newcol = pd.DataFrame(filter)
        df_newcol = df_newcol.reset_index().drop(columns="index")
        pv[i] = df_newcol
    pv.columns = range(1,25)
    return pv


def from_raw(raw):
    '''Convert raw data to the appropriate form'''
    raw[raw<0] = 0
    data = raw * 1_000_000
    data.columns = range(1,25)
    data_mean = data.stack().mean()
    return data, data_mean


def to_series(frame):
    return frame.stack().reset_index(drop=True)
