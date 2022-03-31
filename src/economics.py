'''Economic functions'''

import config


def euro(money):
    '''Nice format for printing money'''
    return format(round(money, 2), ",") + " €"


def presentValueCashflow(cashflow, t, i):
    '''Present value of future cashflow'''
    return cashflow / (1+i)**t


def presentValueStream(cashflow, t, i):
    '''Present value of a cashflow stream'''
    return cashflow * ((1-((1+i)**(-t))) / i)


def lcoe(t, i, n, It, Mt, Ft, Et):
    '''Levelized Cost of Electricity'''
    pass


def NPV(res_initial_cost, energy_production_peryear, battery):
    '''Net Present Value'''
    total_initial_cost = res_initial_cost + battery.cost
    energy_income_peryear = energy_production_peryear * config.wh_sell_price
    onm_cost = total_initial_cost * config.onm

    reinvest_cost = presentValueCashflow(battery.cost, battery.lifespan, config.discount_rate)
    positive_stream = presentValueStream(energy_income_peryear, config.project_lifetime, config.discount_rate)
    negative_stream = presentValueStream(onm_cost, config.project_lifetime, config.discount_rate)

    npv = positive_stream - negative_stream - reinvest_cost - total_initial_cost
    costs = negative_stream + reinvest_cost + total_initial_cost
    return npv, negative_stream, reinvest_cost, costs
