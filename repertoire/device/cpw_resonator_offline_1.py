import sys

import numpy as np
import datetime

today = str(datetime.date.today()).split('-')
time_stamp = today[0][-2:] + today[1] + today[2]

sys.path.append('../')
from class_chip import chip

import cpw_1 as cpw

def new_device(length=1850, width=200, mode='compact',
                    a=10, b=6, r=50, d_rad=np.pi / 36, layer='Nb_inv'):

    N = int(np.floor(length / ((width - 2 * r) + np.pi * r)))
    length_wiggle = ((width - 2 * r) + np.pi * r) * N
    pre = 0
    post = length - length_wiggle

    # %%
    path = [0, pre]
    for num_1 in range(N):
        if num_1 % 2 == 0:
            path.append(path[-1] + r)
            path.append(path[-1] + 1j * width)
            path.append(path[-1] + r)
        else:
            path.append(path[-1] + r)
            path.append(path[-1] - 1j * width)
            path.append(path[-1] + r)

    geometry_1 = []
    if mode == 'compact':
        rad = np.min([post, np.pi * r / 2]) / r
        if num_1 % 2 == 0:
            pt_ori = path[-1] - 1j * r
            geometry_1 += cpw.cpw_curve(path[-1], pt_ori, -rad, a=a, b=b, d_rad=d_rad)
            end_pt = pt_ori + (path[-1] - pt_ori) * np.exp(-1j * rad)
        else:
            pt_ori = path[-1] + 1j * r
            geometry_1 += cpw.cpw_curve(path[-1], pt_ori, rad, a=a, b=b, d_rad=d_rad)
            end_pt = pt_ori + (path[-1] - pt_ori) * np.exp(1j * rad)

        post += - rad * r
        if post > 0:
            length_wiggle = np.min([post, width - 2 * r])
            if num_1 % 2 == 0:
                geometry_1 += cpw.cpw_straight(end_pt, end_pt - 1j * length_wiggle, a=a, b=b)
                end_pt = end_pt - 1j * length_wiggle
            else:
                geometry_1 += cpw.cpw_straight(end_pt, end_pt + 1j * length_wiggle, a=a, b=b)
                end_pt = end_pt + 1j * length_wiggle

        post += - length_wiggle
        if post > 0:
            rad = np.min([post, np.pi * r / 2]) / r
            if num_1 % 2 == 0:
                geometry_1 += cpw.cpw_curve(end_pt, end_pt + r, rad, a=a, b=b, d_rad=d_rad)
                end_pt = (end_pt + r) - r * np.exp(1j * rad)
            else:
                geometry_1 += cpw.cpw_curve(end_pt, end_pt + r, -rad, a=a, b=b, d_rad=d_rad)
                end_pt = (end_pt + r) - r * np.exp(-1j * rad)
    else:
        end_pt = path[-1] + post
        path.append(end_pt)

    path = np.array(path)
    cpw_1 = cpw.new_device(path, a=a, b=b, r=r, d_rad=d_rad, layer=layer)
    cpw_1.add_geometry(layer, geometry_1)

    cpw_1.add_port('1', path[0])
    cpw_1.add_port('2', end_pt)

    return cpw_1

x = new_device()

chip_1 = chip(name='cpw_resonator_offline',
              time=time_stamp,
              logo='QCD',
              die_size=(15e3, 15e3),
              chip_size=(10e3, 10e3),
              trap_size=(20, 100))

chip_1.add_device('cpw_resonator_offline', x, ref=5e3 * (1 + 1j), degree=0, axis='none', port='1')
chip_1.gen_gds(marker=True, flux_trap=True, set_zero=False)
