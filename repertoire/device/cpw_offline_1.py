import numpy as np
import scipy as sci

import datetime
import sys
import os

today = str(datetime.date.today()).split('-')
time_stamp = today[0][-2:] + today[1] + today[2]
device_name = os.path.basename(__file__)[:-3]

sys.path.append('../')
from class_device import device
from class_chip import chip
import aux_poly

#%% dependence
import cpw_1 as cpw

#%% design
def new_device(
        pt_start=0,
        pt_stop=1000,
        length=3000,
        N=0,
        flip=False,
        zero_pre=False,
        a=10,
        b=6,
        r=50,
        d_rad=np.pi / 36,
        layer='Nb_inv'):
    dx = np.abs(pt_stop - pt_start)
    ph_x = np.angle(pt_stop - pt_start)

    length = np.round(length, 3)

    def func(theta, N):
        return theta - np.sin(theta) - (length - dx) / (2 * (N + 1) * r)

    if N == 0:
        N = int(np.floor(dx / (2 * r)) - 1)
        N = int(2 * np.ceil(N / 2) - 1)

        length_wiggle = length - (dx - 2 * r * (N + 1))
        width = length_wiggle / (N + 1) + 2 * r - np.pi * r
        while (width < 2 * r) and (N >= 2):
            N += -2
            length_wiggle = length - (dx - 2 * r * (N + 1))
            width = length_wiggle / (N + 1) + 2 * r - np.pi * r

        theta = np.pi / 2
        length_wiggle = length - (dx - 2 * r * (N + 1))
        width = length_wiggle / (N + 1) + 2 * r - np.pi * r

        if (width < 2 * r):
            N = int(np.floor(dx / (2 * r))) - 1
            N = int(2 * np.ceil(N / 2) - 1)

            res = sci.optimize.root(func, 0, args=(N,))
            theta = np.squeeze(res.x)

            N_new = int(np.floor(dx / (2 * r * np.sin(theta)))) - 1 if (theta != 0) else 1
            N_new = int(2 * np.ceil(N_new / 2) - 1)

            while N_new != N:
                N = np.copy(N_new)
                res = sci.optimize.root(func, 0, args=(N,))
                theta = np.squeeze(res.x)

                if theta <= 0.1 * np.pi / 180:
                    N_new = 1
                    N = 1
                else:
                    N_new = int(np.floor(dx / (2 * r * np.sin(theta))) - 1)

                N_new = int(2 * np.ceil(N_new / 2) - 1)

            length_wiggle = 2 * (N + 1) * r * theta
            width = 0

    else:
        N = int(2 * np.ceil(N / 2) - 1)

        theta = np.pi / 2
        length_wiggle = length - (dx - 2 * r * (N + 1))
        width = length_wiggle / (N + 1) + 2 * r - np.pi * r

        if (width < 2 * r):
            res = sci.optimize.root(func, 0, args=(N,))
            theta = np.squeeze(res.x)
            length_wiggle = 2 * (N + 1) * r * theta
            width = 0

    if zero_pre:
        pre = 0
        post = (length - length_wiggle)
    else:
        pre = (length - length_wiggle) / 2
        post = (length - length_wiggle) / 2

    x1 = r * np.tan(theta / 2)
    x2 = 2 * r * np.sin(theta) - 2 * x1
    if (theta == np.pi / 2):
        y2 = width
    else:
        y2 = r - r * (2 * np.cos(theta) - 1)

    # %%
    path = [0, pre]
    for num_1 in range(N + 1):
        if num_1 % 2 == 0:
            path.append(path[-1] + x1)
            # path.append(path[-1] + 1j * width)
            path.append(path[-1] + (x2 + 1j * y2))
            path.append(path[-1] + x1)
        else:
            path.append(path[-1] + x1)
            path.append(path[-1] + (x2 - 1j * y2))
            # path.append(path[-1] - 1j * width)
            path.append(path[-1] + x1)

    end_pt = path[-1] + post
    path.append(end_pt)

    if flip:
        path = np.conjugate(path)

    path = np.array(path) * np.exp(1j * ph_x) + pt_start
    cpw_1 = cpw.new_device(path, a=a, b=b, r=r, d_rad=d_rad, layer=layer)

    return cpw_1

#%% example
x = new_device(pt_start=0, pt_stop=1050,
               length=1050)

chip_1 = chip(name=device_name,
              time=time_stamp,
              logo='QCD',
              die_size=(15e3, 15e3),
              chip_size=(10e3, 10e3),
              trap_size=(20, 100))

chip_1.combine_device(x, ref=5e3 * (1 + 1j), degree=0, axis='none', port='1')
chip_1.gen_gds(marker=True, flux_trap=True, set_zero=True)
