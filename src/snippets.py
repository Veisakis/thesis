import scipy.optimize as spo

def f(x):
    return x**2 + 2*x - 5

x_search = 0
result = spo.minimize(f, x_search)

print(f'Minimum is f(x)= {result.fun:.2} at x= {result.x[0]:.2}')

with open('/home/manousos/myfiles/thesis/data/battery.json', 'r') as f:
    bat = json.load(f)

    bat_energy_percycle = bat['voltage'] * bat['capacity'] * bat['dod']
    bat_energy_perlifetime = bat_energy_percycle * bat['cycles']
    print("Battery can store {} kWh in it's lifetime".format(bat_energy_perlifetime))


print("\nChoose examination timespan:")
timespan_selection = int(input("[1] Day\n[2] Year\n"))

while timespan_selection > 2 or timespan_selection < 1:
    print("\nInvalid answer. Please choose one of the below:")
    timespan_selection = int(input("[1] Daily\n[2] Yearly\n"))


### Test Sample: Battery and Daily Gridload-PV
bat1 = Battery.from_json("/home/manousos/myfiles/thesis/data/lead_carbon.json")

gridload_raw = pd.read_csv("/home/manousos/myfiles/thesis/data/moires_gridload.csv", sep=":")
gridload = (gridload_raw.drop(gridload_raw.columns[0:2], axis=1).mean()) * 1_000_000

pv_raw = pd.read_csv("/home/manousos/myfiles/thesis/data/pv_production.csv")
pv_raw['P'] = pv_raw['P'] * 1000
pv_raw['P'] = pv_raw['P'] * 20
pv = pv_raw['P'].iloc[::24]
pv = pv.to_frame().rename(columns={'P': 0}).reset_index().drop(columns="index")

for i in range(1,24):
    filter = pv_raw['P'].iloc[i::24]
    df_newcol = pd.DataFrame(filter)
    df_newcol = df_newcol.reset_index().drop(columns="index")
    pv[i] = df_newcol

pv = pv.mean()
###

wasted_energy = wasted_energy(gridload, pv)
numBatteries = bat1.batteriesNeeded(wasted_energy)
print(wasted_energy, numBatteries)

bat1.batteryPack(numBatteries)
print(bat1.nominal_power)
gridload_flattened = flattenCurve(gridload, 1_000_000, bat1)
import logging

logging.basicConfig(filename="thesis.log",
                    level=logging.DEBUG,
                    format="%(levelname)s: %(message)s",
                    filemode='w')

logger = logging.getLogger()
logger.info("Hello Log!")
logger.debug("Variable a has value of 10")

def formatData(pv_raw, gridload_raw):
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

print("Choose storage method:")
method = int(input("[1] Store all energy produced\n"
                   + "[2] Store only excess energy\n"))

while method > 2 or method < 1:
    print("\nInvalid answer. Please choose one of the below:")
    method = int(input("[1] Store all energy produced\n"
                       + "[2] Store only excess energy\n"))
                       
if method == 1:
    solar_energy = processData.solarProduction(pv)
    solar_batteries = bat.batteriesNeeded(solar_energy)

    formatted_solar_energy = format(round(solar_energy, 2), ",")

    print(f'Daily Solar Production (Wh){formatted_solar_energy:.>60}')
    print(f'Batteries Required to Store this energy{solar_batteries:.>48}\n')

    minimum_batteries, optimizedBatteryPack, gridload_mean, gridload_flattened = processData.batteriesOptimize(target_batteries,
                                                                                                               solar_batteries, gridload, bat_type)


def formatData(pv_raw, gridload_raw):
    pv = pv_raw['P']
    gridload = gridload_raw.drop(gridload_raw.columns[0:2], axis=1).stack().reset_index(drop=True) * 1_000_000
    return pv, gridload
    
    
    
    
'''
target_energy = processData.targetEnergy(gridload)
target_batteries = bat.batteriesNeeded(target_energy)

formatted_target_energy = format(round(target_energy, 2), ",")

print(f'Energy Required to flatten the Curve (Wh){formatted_target_energy:.>46}')
print(f'Batteries Required to Store this energy{target_batteries:.>48}\n')


solar_energy = processData.solarProduction(pv)
excess_solar_energy = processData.wastedEnergy(pv, gridload)
solar_batteries = bat.batteriesNeeded(excess_solar_energy)

formatted_solar_energy = format(round(solar_energy, 2), ",")
formatted_excess_solar_energy = format(round(excess_solar_energy, 2), ",")

print(f'Daily Solar Production (Wh){formatted_solar_energy:.>60}')
print(f'Excess Daily Solar Production (Wh){formatted_excess_solar_energy:.>53}')
print(f'Batteries Required to Store this excess energy{solar_batteries:.>41}\n')

minimum_batteries, optimizedBatteryPack, gridload_mean, gridload_flattened = processData.batteriesOptimize(target_batteries, solar_batteries,
                                                                                                               processData.solarAid(pv, gridload), bat_type)                                                                                                           


print(f'\n{"Optimization Results":-^65}')
print(f'Batteries: {minimum_batteries}')
print(f'State of Charge (after grid stabilization): {optimizedBatteryPack.stateOfCharge()*100 if minimum_batteries != 0 else 0:.2f}%')
print(f'Total Cost: {format(optimizedBatteryPack.cost * minimum_batteries, ",")}€\n')
'''


def solarProduction(pv):
    return pv.sum()


def wastedEnergy(pv, gridload, battery):
    balance = np.array(pv) - np.array(gridload)
    excess_energy = balance[balance > 0]
    for energy in excess_energy:
        if battery.canCharge(energy) == 1:
            battery.charge(energy)
    return excess_energy.sum()


def targetEnergy(gridload, deviation):
    energy = 0
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


def batteriesOptimize(target, production, gridload, bat_type):
    if target > production:
        optimization_range = [production]
    else:
        optimization_range = range(target, production+1)

    for batteries in optimization_range:
        testBat = Battery.from_json(bat_type)
        testBat.batteryPack(batteries)

        gridload_mean, gridload_flattened, deviation = flattenCurve(gridload, testBat)
        if len(deviation[deviation > 0]) == 0:
            break
    return batteries, testBat, gridload_mean, gridload_flattened