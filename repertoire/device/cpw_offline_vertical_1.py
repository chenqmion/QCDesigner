import sys

import numpy as np
import datetime

from scipy.optimize import root

today = str(datetime.date.today()).split('-')
time_stamp = today[0][-2:] + today[1] + today[2]

sys.path.append('../')
from class_chip import chip

import cpw_1 as cpw

def new_device(
        length=3000,
        N=3,
        flip=False,
        a=10,
        b=6,
        r=50,
        d_rad=np.pi / 36,
        layer='Nb_inv'):

    length = np.round(length, 3)
    width = (length + np.pi*r) / (N+1) + 2 * r - np.pi * r

    # %%
    path = [0, 1j*(width-2*r)]
    for num_1 in range(N):
        if num_1 % 2 == 0:
            path.append(path[-1] + 1j * r)
            path.append(path[-1] + 2*r)
            path.append(path[-1] - 1j * (width-r))
        else:
            path.append(path[-1] - 1j * r)
            path.append(path[-1] + 2*r)
            path.append(path[-1] + 1j * (width-r))

    if flip:
        path = np.conjugate(path)

    cpw_1 = cpw.new_device(path, a=a, b=b, r=r, d_rad=d_rad, layer=layer)

    cpw_1.add_port('1', path[0])
    cpw_1.add_port('2', path[-1])

    return cpw_1

x = new_device(length=1050)

chip_1 = chip(name='cpw_offline_vertical',
              time=time_stamp,
              logo='QCD',
              die_size=(15e3, 15e3),
              chip_size=(10e3, 10e3),
              trap_size=(20, 100))

chip_1.add_device('cpw_offline', x, ref=5e3 * (1 + 1j), degree=0, axis='none', port='1')
chip_1.gen_gds(marker=True, flux_trap=False, set_zero=False)
