plt.style.use('classic')
fig, (ax1, ax2) = plt.subplots(nrows=2, ncols=1)

ax1.plot(timespan, pv, linestyle='dashed',
         color='darkolivegreen', label='PV power output')
ax1.plot(timespan, gridload,
         color='saddlebrown', label='Grid Load')

ax1.fill_between(timespan, pv, gridload,
                 where=(pv > gridload), interpolate=True,
                 color='yellowgreen', alpha=0.40, label='Excess Energy')

ax1.set_xticks(timespan)
ax1.set_xlim(timespan[0], timespan[-1])

ax1.set_ylabel('Power (W)')
ax1.set_title('Grid load and PV power output curves')

ax1.grid(True)
ax1.legend(loc='upper left')


ax2.plot(timespan, gridload,
         color='saddlebrown', label='Grid Load without battery storage')
ax2.plot(timespan, gridload_flattened,
         color='darkolivegreen', label='Grid Load with battery storage')

ax2.fill_between(timespan, gridload, color='saddlebrown', alpha=0.50)
ax2.fill_between(timespan, gridload_flattened, color='olive', alpha=0.30)

ax2.set_xticks(timespan)
ax2.set_xlim(timespan[0], timespan[-1])

ax2.set_xlabel('Hour of the day (h)')
ax2.set_ylabel('Power (W)')
ax2.set_title('Grid load "with" and "without" Batteries')

ax2.grid(True)
ax2.legend(loc='upper left')

plt.tight_layout()
plt.show()