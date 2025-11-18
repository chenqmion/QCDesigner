import sys

import numpy as np
import datetime

today = str(datetime.date.today()).split('-')
time_stamp = today[0][-2:] + today[1] + today[2]

sys.path.append('../')
from class_chip import chip

import cpw_1 as cpw


def new_device(pt_start=0, pt_stop=None,
                   length=1000, width=0, N=0,
                   a=10, b=6, r=50, d_rad=np.pi / 36, layer='Nb_inv'):
    if pt_stop == None:
        ph_x = 0
    else:
        dx = pt_stop - pt_start
        ph_x = np.angle(dx)
        if (N == 0):
            length = np.abs(dx)

    if N == 0:
        width = 0
        pre = length / 2
        post = length / 2
    else:
        if width == 0:
            pre = r
            post = r
            width = (length - np.pi * r + 2 * r) / N - np.pi * r + 2 * r
        else:
            length_1 = ((width - 2 * r) + np.pi * r) * N - 2 * r + np.pi * r
            pre = (length - length_1) / 2 + r
            post = (length - length_1) / 2 + r

    # %%
    path = [0, pre]

    for num_1 in range(N):
        if num_1 % 2 == 0:
            path.append(path[-1] + 1j * (width / 2))
            path.append(path[-1] + 2 * r)
            path.append(path[-1] - 1j * (width / 2))
        else:
            path.append(path[-1] - 1j * (width / 2))
            path.append(path[-1] + 2 * r)
            path.append(path[-1] + 1j * (width / 2))

    path.append(path[-1] + post)
    path = np.array(path) * np.exp(1j * ph_x) + pt_start
    cpw_1 = cpw.new_device(path, a=a, b=b, r=r, d_rad=d_rad, layer=layer)

    cpw_1.add_port('1', path[0])
    cpw_1.add_port('2', path[-1])

    return cpw_1


x = new_device(pt_start=0, pt_stop=1000,
               width=400,
               length=1000, N=2)

chip_1 = chip(name='cpw_resonator_inline',
              time='250611',
              logo='QCD',
              die_size=(15e3, 15e3),
              chip_size=(10e3, 10e3),
              trap_size=(20, 100))
chip_1.add_device('cpw_inline', x, ref=5e3 * (1 + 1j), degree=0, axis='none', port='1')
chip_1.gen_gds(marker=True, flux_trap=True, set_zero=True)
