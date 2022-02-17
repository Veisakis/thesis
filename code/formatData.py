try:
    gridload_raw = pd.read_csv(path + "/data/moires_gridload.csv", sep=":")
except FileNotFoundError as err:
    print(err)

try:
    pv_raw = pd.read_csv(path + "/data/pv_production.csv")
except FileNotFoundError as err:
    print(err)


def daily():
    global timespan, gridload, pv
    gridload = (gridload_raw.drop(gridload_raw.columns[0:2], axis=1).mean()) * 1_000_000

    pv_raw['P'] = pv_raw['P'] * 1000
    pv = pv_raw['P'].iloc[::24]
    pv = pv.to_frame().rename(columns={'P': 0}).reset_index().drop(columns="index")

    for i in range(1, 24):
        filter = pv_raw['P'].iloc[i::24]
        df_newcol = pd.DataFrame(filter)
        df_newcol = df_newcol.reset_index().drop(columns="index")
        pv[i] = df_newcol

    pv = pv.mean()
    timespan = range(24)


def yearly():
    global timespan, gridload, pv
    gridload = (gridload_raw.drop(gridload_raw.columns[0:2], axis=1).stack().array) * 1_000_000

    pv = pv_raw['P']
    timespan = range(8760)


if ts == 1:
    daily()
else:
    yearly()
