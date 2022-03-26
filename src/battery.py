'''Representation of single battery or battery pack'''

import json
import math


class Battery:
    def __init__(self, type, voltage, capacity_wh, efficiency,
                 cycles, dod, cost_per_wh, lifespan, isbattery_pack=0, number=1):
        self.type = type
        self.voltage = voltage
        self.efficiency = efficiency
        self.cycles = cycles
        self.dod = dod

        self.nominal_capacity = capacity_wh
        self.max_capacity = self.nominal_capacity * self.dod
        self.min_capacity = self.nominal_capacity * (1-self.dod)
        self.capacity = self.min_capacity

        self.cost = self.nominal_capacity * cost_per_wh
        self.lifespan = lifespan

        self.isbattery_pack = isbattery_pack
        self.number = number

    def __str__(self):
        if self.isbattery_pack == 0:
            return f'{self.nominal_capacity / 1000} kWh {self.type} battery.'
        else:
            return f'{self.nominal_capacity / 1_000_000} MWh {self.type} battery pack.'

    def batteriesNeeded(self, energy):
        return math.ceil(energy / self.max_capacity)

    def batteryPack(self, number, inSeries=1):
        assert number > 0, "Cannot be less than 1 battery in a pack!"
        assert inSeries > 0, "Cannot be less than 1 battery in series!"

        self.voltage = self.voltage * inSeries

        self.nominal_capacity = self.nominal_capacity * number
        self.capacity = self.min_capacity * number

        self.number = number
        self.isbattery_pack = 1
        self.cost = self.cost * number

    def charge(self, energy):
        potential_soc = (self.nominal_capacity - self.capacity + energy) / self.nominal_capacity
        if potential_soc > 1:
            self.capacity = self.max_capacity
            return 0
        else:
            self.capacity += energy
            return energy

    def discharge(self, energy):
        potential_soc = (self.nominal_capacity - self.capacity - energy) / self.nominal_capacity
        if potential_soc < self.dod:
            energy = self.capacity - self.min_capacity
            self.capacity = self.min_capacity
            return energy
        else:
            self.capacity -= energy
            return energy

    def stateOfCharge(self):
        return self.capacity / self.nominal_capacity

    @classmethod
    def from_json(cls, json_path):
        with open(json_path, 'r') as f:
            data = json.load(f)

        return cls(data['type'], data['voltage'], data['capacity_wh'],
                   data['efficiency'], data['cycles'], data['dod'],
                   data['cost_per_wh'], data['lifespan'])
