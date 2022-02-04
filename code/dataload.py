import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from request import path

gridload = pd.read_csv(path + "/data/moires_gridload.csv", sep=":")
pv = pd.read_csv(path + "/data/pv_formatted.csv")

y_grid = gridload.drop(gridload.columns[0:2], axis=1).stack().array
y_pv = pv['P'].array / 1_000_000 # converting to MW from W
x = range(8760)

plt.plot(x, y_grid)
plt.plot(x, y_pv)
plt.show()


balance = np.array(y_pv - y_grid)

positive_energy_sum = balance[balance > 0].sum()
positive_energy_hours = balance[balance > 0].size
excess_energy = positive_energy_sum * positive_energy_hours

print(f'\n{excess_energy:.3} MWh are wasted!')
