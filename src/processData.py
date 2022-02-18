import numpy as np
import pandas as pd


def conditionalFormatting(pv_raw, gridload_raw, timespan_selection):
    if timespan_selection == 1:
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
        timespan = range(24)

    else:
        pv = pv_raw['P']
        gridload = (gridload_raw.drop(gridload_raw.columns[0:2], axis=1)) * 1_000_000
        gridload = gridload.stack().reset_index(drop=True)
        timespan = range(8760)

    return pv, gridload, timespan


def wastedEnergy(pv, gridload):
    balance = np.array(pv) - np.array(gridload)

    excess_power = balance[balance > 0].sum()
    excess_power_duration = balance[balance > 0].size
    excess_energy = excess_power * excess_power_duration

    return excess_energy


def flattenCurve(gridload, power, battery):
    deviation = np.abs(gridload - gridload.mean())

    while battery.stateOfCharge() > battery.dod:
        deviation[deviation.argmax()] = deviation.max() - power
        battery.discharge(power * 1)

    return deviation
