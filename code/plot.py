plt.style.use('classic')

plt.plot(timespan, gridload)
plt.plot(timespan, pv)

plt.xlabel('Hour')
plt.ylabel('Power (W)')
plt.title('Grid load and PV power output curves')

plt.grid(True)
plt.legend(['Grid Load',
            'PV power output'])


plt.plot(timespan, gridload)
plt.plot(timespan, gridload_flattened)

plt.xticks(timespan)

plt.xlabel('Hour of the day (h)')
plt.ylabel('Grid Load (W)')
plt.title('Grid load "with" and "without" Batteries')

plt.grid(True)
plt.legend(['Grid Load without battery storage',
            'Grid Load with battery storage'])



plt.show()
