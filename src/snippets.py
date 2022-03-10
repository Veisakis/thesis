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
