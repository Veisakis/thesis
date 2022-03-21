import numpy as np
import pandas as pd

from battery import Battery


def formatData(pv_raw, gridload_raw):
    '''Convert raw data to the appropriate form'''
    gridload = gridload_raw.drop(gridload_raw.columns[0:2], axis=1).reset_index(drop=True) * 1_000_000
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
        if battery.canCharge(energy) == 1:
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
        if battery.stateOfCharge() > battery.dod and deviation[index] > 0:
            energy = deviation[index]
            if battery.canDischarge(energy) == 0:
                continue

            deviation[index] = 0
            gridload_sample[index] -= energy
            battery.discharge(energy)
    return gridload_sample


def simResults(gridload, gridload_mean, battery):
    '''Calculate how much has the curve flattened, based on the distance from the median'''
    energy = 0
    deviation = gridload - gridload_mean
    sortedIndeces = np.flip(np.argsort(deviation))
    for index in sortedIndeces:
        if deviation[index] > 0:
            energy += deviation[index]
    return energy


def batteryOptimization(pv, gridload, gridload_mean, sample_min, sample_max, battery):
    '''Run all the above functions, for each scenario of battery-pack size'''
    print(f'\n{"Batteries":<10}{"System Cost":>25}{"Energy Left":>40}\n')
    
    batteries_sample = list(range(sample_min, sample_max))
    for batteries in batteries_sample:
        battery.batteryPack(batteries)
        gridload_flat = []
        
        for day in range(365):
            pv_day = pv.iloc[day]
            gridload_day = gridload.iloc[day]
            wastedEnergy(pv_day, gridload_day, battery)
            gridload_day = solarAid(pv_day, gridload_day)
            gridload_flt = flattenCurve(gridload_day, gridload_mean, battery)
            gridload_flat.append(gridload_flt)
        
        df = pd.DataFrame(gridload_flat)
        gridload_flattened = df.stack().reset_index(drop=True)

        energy_left = simResults(gridload_flattened, gridload_mean, battery)
        print(f'{battery.number:<10}\t{format(battery.cost, ","):^20} €\t{format(energy_left, ","):>40} Wh')
        
        if energy_left == 0:
            pv = pv.stack().reset_index(drop=True)
            gridload = gridload.stack().reset_index(drop=True)
            return pv, gridload, gridload_flattened, battery
            
            
            