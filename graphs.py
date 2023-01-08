import numpy as np
import matplotlib.pyplot as plt

time = np.array(range(24))

load = np.array([7, 8, 9.9, 9.3, 9, 8.9, 9, 8.8, 9.1, 9.4, 11.2, 12.3, 13.2, 12.2, 10.4, 10, 10.6, 12.9, 14.2, 14.3, 14.1, 13.5, 12.4, 11.6])
pv   = np.array([0, 0, 0, 0, 0, 0, 1, 3, 6, 9, 12, 15, 16, 17, 17, 16, 14, 11, 9, 5, 2, 0, 0, 0])
wt   = np.array([3, 2, 1.1, 2.7, 4.5, 1.2, 5.7, 3, 2, 2, 1, 0, 1, 0, 4, 2, 1, 0, 7.6, 3.1, 4, 1, 1, 5])

#for i in range(24):
#    if pv[i] >= load[i]:
#        pv[i] = load[i]

load = load - pv - wt

#plt.fill_between(time, load, pv, where=(pv > load), interpolate=True, color='seagreen', alpha=0.4)
plt.plot(time, load, color='darkslategrey', linestyle='--')
load[load >= 5] = 5
plt.plot(time, load)
#plt.plot(time, pv, color='tomato')
#plt.plot(time, wt, color='deepskyblue')

#plt.axhline(y=7, linestyle='--')

plt.yticks([])
plt.grid()
plt.show()
