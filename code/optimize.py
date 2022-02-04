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
