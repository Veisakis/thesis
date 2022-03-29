import os
import sys
import requests
import numpy as np
import pandas as pd

import config


def csv(name):
    '''Get gridload data for a specific location, from csv files saved in data folder'''
    filename = config.path + "/thesis/data/" + name + "_gridload.csv"
    try:
        gridload_raw = pd.read_csv(filename, sep=":")
    except FileNotFoundError:
        print(f'File {filename} not found!')
        sys.exit()
    else:
        print("Loaded gridload data for the area.")
        return gridload_raw
        
        
def pvgis(lat, lon, solar):
    '''
    Get solar hourly production data for a year from pv-gis API, 
    for a specific location and specific solar system size
    ''' 
    print("\nFetching PV data from PV-GIS...")
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
        print("Connection Established!\n")
        os.system("curl \'"+url+"\' | tail -n+11 | head -n-11 >" +
                  config.path+"/thesis/data/pv_production.csv")
        print("\nSaved solar data to file pv_production.csv")

    try:
        pv_raw = pd.read_csv(config.path + "/thesis/data/pv_production.csv")
    except FileNotFoundError as err:
        sys.exit(err)
    return pv_raw


def formatData(pv_raw, gridload_raw):
    '''Convert raw data to the appropriate form'''
    gridload = gridload_raw.drop(
        gridload_raw.columns[0:2], axis=1).reset_index(drop=True) * 1_000_000
    gridload.columns = list(range(24))
    gridload_mean = gridload.stack().mean()

    pv = pv_raw['P'].iloc[::24]
    pv = pv.to_frame().rename(columns={'P': 0}).reset_index().drop(columns="index")

    for i in range(1, 24):
        filter = pv_raw['P'].iloc[i::24]
        df_newcol = pd.DataFrame(filter)
        df_newcol = df_newcol.reset_index().drop(columns="index")
        pv[i] = df_newcol
    return pv, gridload, gridload_mean


def datagovgr():
    '''Fetch data for all of Greece, from data.gov.gr API'''
    url = 'https://data.gov.gr/api/v1/query/admie_realtimescadares?date_from=2021-01-01&date_to=2021-12-31'
    headers = {'Authorization': 'Token cae197251734baf5d81483596ac52d81cb41b779'}

    r = requests.get(url, headers=headers)

    df_raw = pd.DataFrame(r.json())
    df_raw = df_raw.drop('date', axis=1)

    df = df_raw.iloc[::24]
    df = df.rename(columns={'energy_mwh': 0}).reset_index().drop(columns="index").drop(364)

    for i in range(1, 24):
        filter = df_raw.iloc[i::24]
        df_newcol = pd.DataFrame(filter)
        df_newcol = df_newcol.reset_index().drop(columns="index")
        df[i] = df_newcol['energy_mwh']
    res = df

    url = 'https://data.gov.gr/api/v1/query/admie_realtimescadasystemload?date_from=2021-01-01&date_to=2021-12-31'
    headers = {'Authorization': 'Token cae197251734baf5d81483596ac52d81cb41b779'}

    r = requests.get(url, headers=headers)

    df_raw = pd.DataFrame(r.json())
    df_raw = df_raw.drop('date', axis=1)

    df = df_raw.iloc[::24]
    df = df.rename(columns={'energy_mwh': 0}).reset_index().drop(columns="index").drop(364)

    for i in range(1, 24):
        filter = df_raw.iloc[i::24]
        df_newcol = pd.DataFrame(filter)
        df_newcol = df_newcol.reset_index().drop(columns="index")
        df[i] = df_newcol['energy_mwh']
    gridload = df
    gridload_mean = np.array(df_raw).mean()

    return res, gridload, gridload_mean
