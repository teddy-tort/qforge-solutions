import sympy as sym
from sympy.abc import z, lamda
from sympy.abc import x as z_0
from sympy.abc import y as w_0
import numpy as np
from print_uncertainty import print_uncertainty as print_u

w_expr = w_0 * sym.sqrt(1 + ((z - z_0) / (sym.pi * w_0 ** 2 / lamda))**2)
wrt = (z, lamda, z_0, w_0)
vals = (2, 632.8e-9, -.03, 1.9e-6)
uncs = (.005, 0.1e-9, .04, 0.09e-6)
w = w_expr.evalf(subs=dict(zip(wrt, vals)))     # value of z evaluated from the expression

unc_w_terms = np.zeros(len(wrt))      # how many terms in the sum for calculating the uncertainty
for ii, var, uncertainty in zip(range(len(wrt)), wrt, uncs):
    derivative = sym.diff(w_expr, var)
    derivative_at_xy = derivative.evalf(subs=dict(zip(wrt, vals)))
    unc_w_terms[ii] = (derivative_at_xy * uncertainty) ** 2
unc_w = np.sqrt(np.sum(unc_w_terms))

print_u(w, unc_w, "m")

