import numpy as np
from numpy.polynomial import Polynomial

from scipy.optimize import least_squares
import scipy.constants as con

#%%
Al_gap=182E-6 * con.e

#%%
def R2L(R, gap=Al_gap):
    L = con.hbar/(np.pi * gap) * R
    return L

def L2R(L, gap=Al_gap):
    R = L / (con.hbar/(np.pi * gap))
    return R

#%%
def x2R(params, x):
    R = params[1] * x + params[0]
    return R

def R2x(params, R):
    # fun_R = Polynomial(params)
    x = params(np.log10(R))
    return 10**x

def res_R(params, x_exp, R_exp):
    R_fit = x2R(params, x=x_exp)
    res = np.log10(R_fit) - np.log10(R_exp)
    return res

def fit_R(x_exp, R_exp, order=1):
    if order == 1:
        params_ini = np.zeros(2)
        params_ini[0] = np.min(R_exp)
        params_ini[1] = (np.median(R_exp) - params_ini[0])/(np.median(R_exp) - np.min(x_exp))

        res_fit = least_squares(res_R, params_ini, args=(x_exp, R_exp))
        y = res_fit.x
        # y = Polynomial.fit(x_exp, R_exp, 1).convert().coef
    else:
        y = Polynomial.fit(np.log10(R_exp), np.log10(x_exp), order)
    return y

#%%
def L2x(params, L, d=1):
    if d == 1:
        R = L2R(L)
        x = R2x(params, R)
    else:
        L1 = 2*L/(1-d)
        R1 = L2R(L1)
        x1 = R2x(params, R1)

        if d == 0:
            x2 = x1
            L2 = L1
        else:
            L2 = (1 - d) / (1 + d) * L1
            R2 = L2R(L2)
            x2 = R2x(params, R2)

        x = [x1, x2]
        L = [L1, L2]
    return [x, L]

