import sys

import numpy as np

sys.path.append('../')
from class_device import device
from class_chip import chip

import aux_poly
import cpw_1 as cpw
import taper_1 as taper

def new_device(length=[10, 50], tip=[1, 20],
               a=10, b=6, a2=3, b2=2, layer='Nv_inv'):

    z = device()
    taper_1 = taper.new_device(length=length[0], a=a, b=b, a2=a2, b2=b2, layer=layer)
    taper_ports = z.combine_device(taper_1, ref=0, port='1')

    cpw1 = cpw.cpw_straight(taper_ports['2'], taper_ports['2'] + length[1] - (a2+b2), a=a2, b=b2)
    z.add_geometry(layer, cpw1)


    poly_1 = [1j * (a2 / 2 + b2)]
    poly_1.append(poly_1[-1] + 1j*tip[0])
    poly_1.append(poly_1[-1]+b2)
    poly_1.append(poly_1[-1] - 1j*tip[0])

    poly_2 = [b2 - 1j * (a2 / 2 + b2)]
    poly_2.append(poly_2[-1] + 1j * b2)
    poly_2.append(poly_2[-1] + a2)
    poly_2.append(poly_2[-1] - 1j * b2)

    poly_3 = [a2 + b2 - 1j * tip[1] / 2]
    poly_3.append(poly_3[-1] + 1j * tip[1])
    poly_3.append(poly_3[-1] + b2)
    poly_3.append(poly_3[-1] - 1j * tip[1])

    z.add_geometry(layer, [poly_1, poly_2, poly_3], ref=taper_ports['2'] + length[1] - (a2+2*b2))

    z.add_port('input', 0)
    z.add_port('output', length[0] + length[1])

    return z

x = new_device()
chip_1 = chip(name='flux',
              time='250611',
              logo='QCD',
              die_size=(15e3, 15e3),
              chip_size=(10e3, 10e3),
              trap_size=(20, 100))
chip_1.add_device('flux', x, ref=5e3 * (1 + 1j), degree=0, axis='none', port='input')
chip_1.gen_gds(marker=True, flux_trap=True, set_zero=True)
