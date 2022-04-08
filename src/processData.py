'''Data manipulation functions'''

import sys
import numpy as np
import pandas as pd

import economics, config
from battery import Battery

year = range(365)


def energyPrettify(energy):
    '''Nice format for printing energy values'''
    return format(round(energy, 2), ",") + " Wh"


def wastedEnergy(res, gridload, battery):
    '''Calculate excess energy produced by renewables and charge the battery with it'''
    balance = np.array(res) - np.array(gridload)
    excess_energy = balance[balance > 0]

    for energy in excess_energy:
        battery.charge(energy)
    return excess_energy.sum()


def resAid(res, gridload):
    '''Subtract energy produced by renewables from the gridload one-by-one'''
    res_sample = np.array(res)
    gridload_sample = np.array(gridload)

    for index in range(len(res_sample)):
        if res_sample[index] > gridload_sample[index]:
            gridload_sample[index] = 0
        else:
            gridload_sample[index] -= res_sample[index]
    return gridload_sample


def flattenCurve(gridload, gridload_mean, battery):
    '''Subtract energy stored in batteries from the gridload's peaks'''
    gridload_sample = np.array(gridload)

    deviation = gridload_sample - gridload_mean
    sortedIndeces = np.flip(np.argsort(deviation))

    for index in sortedIndeces:
        energy = deviation[index]
        if energy > 0:
            discharge_energy = battery.discharge(energy)
            deviation[index] -= discharge_energy
            gridload_sample[index] -= discharge_energy
    return gridload_sample


def isReached(wasted_energy, gridload_aided, gridload_flattened):
    '''Calculate if zero energy waste goal is reached'''
    excess_energy_produced = np.array(wasted_energy).sum()
    energy_supplied = np.array(gridload_aided).sum() - np.array(gridload_flattened).sum()
    return excess_energy_produced - energy_supplied


def batteryOptimization(res, gridload, gridload_mean, sample_min, sample_max, bat_type, res_cost=0, cost_limit=0):
    '''Find optimized result by applying all of the above functions to each battery-pack size'''
    found = 0
    gridload_median = gridload_mean  # Instead of using global
    batteries_sample = list(range(sample_min, sample_max))
    
    res_stack = res.stack().reset_index(drop=True)
    gridload_stack = gridload.stack().reset_index(drop=True)
    
    for batteries in batteries_sample:
        wasted_energy = []
        gridload_aided = []
        gridload_flattened = []

        battery = Battery.from_json(bat_type)
        battery.batteryPack(batteries)
    
        for day in year:
            res_day = res.iloc[day]
            gridload_day = gridload.iloc[day]

            waste_energy = wastedEnergy(res_day, gridload_day, battery)
            gridload_aid = resAid(res_day, gridload_day)
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
        npv, onm, reinvest, costs = economics.NPV(res_cost, res_stack.sum(), battery)
        
        if batteries == sample_min:
            if cost_limit != 0 and costs >= cost_limit:
                sys.exit("Cost limit is too low to find an optimized result for that data.")
            print(f'\nBatteries{"System Cost":>30}{"Energy Wasted":>40}\n')
        
        if gridload_flattened_max <= gridload_median:
            gridload_median = gridload_flattened.mean()

        if cost_limit != 0:    
            battery = Battery.from_json(bat_type)
            battery.batteryPack(batteries+1)
            pot_costs = economics.NPV(res_cost, res_stack.sum(), battery)[3]            
            if pot_costs >= cost_limit:
                found = 1

        if wasted_energy <= 0:
            wasted_energy = 0
            found = 2

        if gridload_flattened_max <= 0:
            found = 3

        print(f'{battery.number:>4}{economics.euro(costs):>36}{energyPrettify(wasted_energy):>42}')

        if found > 0:
            res = res_stack
            gridload = gridload_stack
            return res, gridload, wasted_energy, gridload_aided, gridload_flattened, gridload_median, battery, found, npv, onm, reinvest, costs

    sys.exit("Search Limit reached...\n"
            + "No optimized result was found.\n"
            + "Try using another battery search range from config.py.")
