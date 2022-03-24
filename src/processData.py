'''Data manipulation functions'''

import sys
import numpy as np
import pandas as pd

from battery import Battery

year = range(365)


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


def wastedEnergy(pv, gridload, battery):
    '''Calculate excess energy produced by renewables and charge the battery with it'''
    balance = np.array(pv) - np.array(gridload)
    excess_energy = balance[balance > 0]

    for energy in excess_energy:
        battery.charge(energy)
    return excess_energy.sum()


def solarAid(pv, gridload):
    '''Subtract energy produced by renewables from the gridload one-by-one'''
    pv_sample = np.array(pv)
    gridload_sample = np.array(gridload)

    for index in range(len(pv_sample)):
        if pv_sample[index] > gridload_sample[index]:
            gridload_sample[index] = 0
        else:
            gridload_sample[index] -= pv_sample[index]
    return gridload_sample


def flattenCurve(gridload, gridload_mean, battery):
    '''Subtract energy stored in batteries from the gridload's peaks'''
    gridload_sample = np.array(gridload)

    deviation = gridload_sample - gridload_mean
    sortedIndeces = np.flip(np.argsort(deviation))

    for index in sortedIndeces:
        energy = deviation[index]
        if energy > 0:
            energy = battery.discharge(energy)
            deviation[index] -= energy
            gridload_sample[index] -= energy
    return gridload_sample


def isReached(wasted_energy, gridload_aided, gridload_flattened):
    '''Calculate if zero energy waste goal is reached'''
    excess_energy_produced = np.array(wasted_energy).sum()
    energy_supplied = np.array(gridload_aided).sum() - np.array(gridload_flattened).sum()
    return excess_energy_produced - energy_supplied


def batteryOptimization(pv, gridload, gridload_mean, sample_min, sample_max, bat_type, cost_limit):
    '''Find optimized result by applying all of the above functions to each battery-pack size'''
    found = 0
    gridload_median = gridload_mean #Instead of using global
    batteries_sample = list(range(sample_min, sample_max))

    print(f'\nBatteries{"System Cost":>30}{"Energy Wasted":>40}\n')

    for batteries in batteries_sample:
        wasted_energy = []
        gridload_aided = []
        gridload_flattened = []
        
        battery = Battery.from_json(bat_type)
        battery.batteryPack(batteries)

        for day in year:
            pv_day = pv.iloc[day]
            gridload_day = gridload.iloc[day]

            waste_energy = wastedEnergy(pv_day, gridload_day, battery)
            gridload_aid = solarAid(pv_day, gridload_day)
            gridload_flat = flattenCurve(gridload_aid, gridload_median, battery)

            wasted_energy.append(waste_energy)
            gridload_aided.append(gridload_aid)
            gridload_flattened.append(gridload_flat)
        
        gridload_aided = pd.DataFrame(gridload_aided)
        gridload_aided = gridload_aided.stack().reset_index(drop=True)
        gridload_flattened = pd.DataFrame(gridload_flattened)
        gridload_flattened = gridload_flattened.stack().reset_index(drop=True)

        gridload_flattened_max = int(gridload_flattened.max())
        gridload_median = int(gridload_median)
        
        wasted_energy = isReached(wasted_energy, gridload_aided, gridload_flattened)
                
        if gridload_flattened_max <= gridload_median:
            gridload_median = gridload_flattened.mean()
            
        if cost_limit != 0:
            if battery.cost >= cost_limit:
                found = 1

        if wasted_energy <= 0:
            wasted_energy = 0
            found = 2
        
        if gridload_flattened_max == 0:
            found = 3
        
        print(f'{battery.number:>4}{format(battery.cost, ","):>33} €{format(wasted_energy, ","):>39} Wh')

        if found > 0:
            pv = pv.stack().reset_index(drop=True)
            gridload = gridload.stack().reset_index(drop=True)
            return pv, gridload, wasted_energy, gridload_aided, gridload_flattened, gridload_median, battery, found
    
    sys.exit("Search Limit reached...\nTry using another search range.")