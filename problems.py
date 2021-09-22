from scipy.optimize import minimize

def objective(x):
    return -x[0] * x[1]

def constraint(x):
    return x[0] + x[1] - 8

bnds = ((None, None), (None, None))
cons = {'type': 'eq', 'fun': constraint}
x0 = (2, 2)

res = minimize(
    objective,
    x0,
    method='SLSQP',
    bounds=bnds,
    constraints=cons)

print(res)
