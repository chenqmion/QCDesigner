import sys

import numpy as np
import datetime

today = str(datetime.date.today()).split('-')
time_stamp = today[0][-2:] + today[1] + today[2]

sys.path.append('../')
from class_chip import chip

import cpw_1 as cpw
import cpw_offline_1 as cpw_offline
import lambda4_1 as lambda4

def new_device(ro_length=[2500, 800],
               purcell_length=[2500, 800, 400],
               a=10, b=6, r=50, d_rad=np.pi / 36, layer='Nb_inv'):

    x_c = 2 * r
    w = 2 * r

    purcell_width_1 = 4 * r + (w + a + 2 * b)
    ro_width = 4 * r

    ro_height = ro_length[1] - (purcell_width_1 - r - x_c - (w + a + 2 * b)) - np.pi*r/2 + r
    cpw_1 = lambda4.new_device(length=ro_length[0], height=[ro_height,r], width=(ro_width, 2 * r), mode='compact',
               a=a, b=b, r=r, d_rad=d_rad, layer=layer)

    purcell_height_1 = purcell_length[1] - (x_c-r) - np.pi*r/2 + r
    purcell_length_2 = purcell_length[0] - purcell_length[1] - ((purcell_width_1-2*r) - (x_c-r) + (w+a+2*b) + np.pi * r / 2)
    cpw_2 = lambda4.new_device(length=purcell_length_2, height=[ro_height/2, r], width=(4 * r, 2 * r), mode='incompact',
                               a=a, b=b, r=r, d_rad=d_rad, layer=layer)

    cpw_2_ports = cpw_1.combine_device(cpw_2, ref=cpw_1.ports['3'] + (ro_width/2 + (w + a + 2 * b) - 1j * r), degree=180,
                                       axis='none', port='1')

    path = [0]
    path.append(path[-1] + 1j * ((w + a + 2 * b) + r))
    path.append(path[-1] - purcell_width_1)
    path.append(path[-1] + 1j * purcell_height_1)
    cpw_3 = cpw.new_device(path, a=a, b=b, r=r, d_rad=d_rad, layer=layer)
    cpw_3_ports = cpw_1.combine_device(cpw_3, ref=cpw_2_ports['1'], degree=0, axis='none', port='1')

    return cpw_1

x = new_device()

chip_1 = chip(name='purcell',
              time='250819',
              logo='QCD',
              die_size=(15e3, 15e3),
              chip_size=(10e3, 10e3),
              trap_size=(20, 100))

chip_1.add_device('purcell', x, ref=5e3 * (1 + 1j), degree=0, axis='none', port='1')
chip_1.gen_gds(marker=True, flux_trap=True, set_zero=False)
