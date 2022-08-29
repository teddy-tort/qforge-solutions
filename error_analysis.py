import sympy as sym
from sympy.abc import x, y
import numpy as np

pm = "\u00B1"       # plus minus symbol unicode

z_expr = x ** 2 + y ** 2    # expression for z
wrt = (x, y)  # with respect to what variables
x_val = 20                  # value of x
del_x = 0.15                # uncertainty of x
y_val = 12                  # value of y
del_y = 0.2                 # uncertainty of y
dels = (del_x, del_y)       # uncertainties for zipping
z_val = z_expr.evalf(subs={x: x_val, y: y_val})     # value of z evaluated from the expression

del_z_terms = np.zeros(len(wrt))      # how many terms in the sum for calculating the uncertainty
for ii, var, uncertainty in zip(range(len(wrt)), wrt, dels):
    derivative = sym.diff(z_expr, var)
    derivative_at_xy = derivative.evalf(subs={x: x_val, y: y_val})
    del_z_terms[ii] = (derivative_at_xy * uncertainty) ** 2
del_z = np.sqrt(np.sum(del_z_terms))

print(f"{z_val} {pm} {del_z}")

