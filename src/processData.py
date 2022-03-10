import numpy as np
import pandas as pd

from battery import Battery


def formatData(pv_raw, gridload_raw):
    pv_raw['P'] = pv_raw['P']
    pv = pv_raw['P'].iloc[::24]
    pv = pv.to_frame().rename(columns={'P': 0}).reset_index().drop(columns="index")

    for i in range(1, 24):
        filter = pv_raw['P'].iloc[i::24]
        df_newcol = pd.DataFrame(filter)
        df_newcol = df_newcol.reset_index().drop(columns="index")
        pv[i] = df_newcol

    pv = pv.mean()
    gridload = (gridload_raw.drop(gridload_raw.columns[0:2], axis=1)) * 1_000_000
    gridload = gridload.mean().reset_index(drop=True)
    return pv, gridload


def solarProduction(pv):
    return pv.sum()


def wastedEnergy(pv, gridload):
    balance = np.array(pv) - np.array(gridload)
    excess_energy = balance[balance > 0].sum()
    return excess_energy


def targetEnergy(gridload):
    energy = 0
    deviation = np.array(gridload) - np.array(gridload).mean()
    sortedIndeces = np.flip(np.argsort(deviation))

    for index in sortedIndeces:
        if deviation[index] > 0:
            energy += deviation[index]
    return energy


def solarAid(pv, gridload):
    pv_sample = np.array(pv)
    gridload_sample = np.array(gridload)
    span = range(len(pv_sample))

    for index in span:
        if pv_sample[index] > gridload_sample[index]:
            gridload_sample[index] = 0
        else:
            gridload_sample[index] -= pv_sample[index]
    return gridload_sample


def flattenCurve(gridload, battery):
    gridload_sample = np.array(gridload)
    gridload_mean = gridload_sample.mean()

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
    return gridload_mean, gridload_sample, deviation


def batteriesOptimize(target, production, gridload):
    if target > production:
        optimization_range = [production]
    else:
        optimization_range = range(target, production+1)

    for batteries in optimization_range:
        testBat = Battery.from_json("/home/manousos/myfiles/thesis/data/lead_carbon.json")
        testBat.batteryPack(batteries)

        gridload_mean, gridload_flattened, deviation = flattenCurve(gridload, testBat)
        if len(deviation[deviation > 0]) == 0:
            break
    return batteries, testBat, gridload_mean, gridload_flattened
