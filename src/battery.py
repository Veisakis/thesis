'''Representation of single battery or battery pack'''

import json
import math


class Battery:
    def __init__(self, type, voltage, capacity_kwh, power_kw,
                 efficiency, cycles, dod, isbattery_pack=0):
        self.type = type
        self.voltage = voltage
        self.nominal_capacity = capacity_kwh * 1000
        self.nominal_power = power_kw * 1000
        self.efficiency = efficiency
        self.cycles = cycles
        self.dod = dod
        self.isbattery_pack = isbattery_pack

        self.capacity = self.nominal_capacity * self.efficiency

    def __str__(self):
        return f'{self.nominal_power} W {self.type} battery'

    def batteriesNeeded(self, energy):
        return math.ceil(energy / self.nominal_capacity)

    def batteryPack(self, number, inSeries=1):
        assert inSeries > 0, "Cannot be less than 1 battery in series!"

        if number < 1:
            print("Battery pack must include more than 1 batteries.")
        else:
            self.type = self.type + " Pack"
            self.voltage = self.voltage * inSeries
            self.nominal_capacity = self.nominal_capacity * number
            self.nominal_power = self.nominal_power * number
            self.isbattery_pack = 1

            self.capacity = self.capacity * number

    def charge(self, energy):
        self.capacity += energy

    def discharge(self, energy):
        self.capacity -= energy

    def stateOfCharge(self):
        return self.capacity / self.nominal_capacity

    @classmethod
    def from_json(cls, json_path):
        with open(json_path, 'r') as f:
            data = json.load(f)

        return cls(data['type'], data['voltage'], data['capacity_kwh'],
                   data['power_kw'], data['efficiency'], data['cycles'], data['dod'])
