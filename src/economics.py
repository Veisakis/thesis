'''Economic functions'''


def presentValueCashflow(money, t, i):
    '''Present value of future cashflow'''
    return money / (1+i)**t


def presentValueStream(money, t, i):
    '''Present value of a cashflow stream'''
    return money * ((1-((1+i)**(-t))) / i)


def lcoe(t, i, n, It, Mt, Ft, Et):
    '''Levelized Cost of Electricity'''
    pass
