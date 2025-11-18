import numpy as np
import scipy.constants as con

def cal_En(E_J, E_C, levels=10):
    E_n = []
    for n_level in range(levels):
        E_n.append((np.sqrt(8*E_J*E_C) * (n_level+1/2) - E_C/2 * (n_level**2 + n_level))/con.h)
    return np.array(E_n)

def cal_E_C(C):
    E_C = con.e**2/(2*C)
    return E_C

def cal_E_J(L):
    E_J = (con.physical_constants['mag. flux quantum'][0]/(2*np.pi))**2/L
    return E_J

def f2E(f, alpha):
    E_C = - con.h * alpha
    C = con.e**2/(2*E_C)
    E_J = (con.h * f + E_C)**2/(8*E_C)
    L = (con.physical_constants['mag. flux quantum'][0]/(2*np.pi))**2/E_J
    return [[L, C], [E_J/con.h, E_C/con.h]]