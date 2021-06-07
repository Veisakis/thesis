from scipy.optimize import minimize

objective = lambda x: x[0]*x[3]*(x[0]+x[1]+x[2])+x[2]


constraint1 = lambda x: x[0]*x[1]*x[2]*x[3]-25.0

def constraint2(x):
    sum_sq = 40
    for i in range(4):
        sum_sq -= x[i]**2
    return sum_sq


x0 = [1, 5, 5, 1]

b = (1,5)
bnds = (b,b,b,b)

con1 = {'type':'ineq', 'fun': constraint1}
con2 = {'type': 'eq', 'fun': constraint2}
cons = [con1, con2]


sol = minimize(objective, x0, method='SLSQP', bounds=bnds, constraints=cons)
print(sol)

