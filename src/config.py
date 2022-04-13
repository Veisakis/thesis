import os

batSearch_start = 1
batSearch_end = 500

plotDay_start = 220
plotDay_end = 240
timespan = range(24*plotDay_start, 24*plotDay_end)

discount_rate = 0.06
project_lifetime = 25

onm = 0.01
wh_sell_price = 0.0002
pv_cost_perkWp = 1_000

loss = "14"
angle = "30"
endyear = "2014"
startyear = "2014"

path = os.environ['HOME']

place_coordinates = {
    1: (35.512, 24.012),
    2: (35.364, 24.471),
    3: (35.343, 25.153),
    4: (35.185, 25.706),
    5: (35.050, 24.877),
    6: (35.008, 25.739),
    7: (35.204, 26.098)
}

place_name = {
    1: "chania",
    2: "rethymno",
    3: "heraklio",
    4: "agnikolaos",
    5: "moires",
    6: "ierapetra",
    7: "shteia"
}
