import numpy as np
import scipy as sci

import datetime
import sys
import os

today = str(datetime.date.today()).split('-')
time_stamp = today[0][-2:] + today[1] + today[2]
device_name = os.path.basename(__file__)[:-3]

sys.path.append('../')
from class_device import device, handshake
from class_chip import chip
import aux_poly

#%% dependence
import cpw_1 as cpw
import cpw_resonator_offline_1 as cpw_resonator_offline

#%% design
def new_device(length=2500, height=(1000, 200), width=(500, 300), mode='incompact',
               a=10, b=6, r=50, d_rad=np.pi / 36, layer='Nb_inv'):
    # PRL 111, 080502 (2013)

    path = [0]
    path.append(1j * height[0])
    path.append(path[-1] - width[0])
    path.append(path[-1] - 1j * height[1])

    cpw_1 = cpw.new_device(path, a=a, b=b, r=r, d_rad=d_rad, layer=layer)

    length_1 = (height[0] + height[1] - 2 * r) + (width[0] - 2 * r) + np.pi * r
    length_2 = length - length_1

    cpw_2 = cpw_resonator_offline.new_device(length=length_2, width=(width[0] - width[1]), mode=mode,
                                             a=a, b=b, r=r, d_rad=d_rad, layer=layer)

    new_ports = cpw_1.combine_device(cpw_2, ref=path[-1], degree=-90)

    print(cpw_1.ports)
    print(new_ports)
    cpw_1.ports['2'] = new_ports['2']
    cpw_1.ports['3'] = handshake(x=- width[0] / 2 + 1j * (height[0]), angle=90)

    return cpw_1

#%% example
x = new_device()

chip_1 = chip(name=device_name,
              time=time_stamp,
              logo='QCD',
              die_size=(15e3, 15e3),
              chip_size=(10e3, 10e3),
              trap_size=(20, 100))

chip_1.combine_device(x, ref=5e3 * (1 + 1j), degree=0, axis='none', port='1')
chip_1.gen_gds(marker=True, flux_trap=True, set_zero=True)
