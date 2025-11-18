import sys

import numpy as np
import datetime

today = str(datetime.date.today()).split('-')
time_stamp = today[0][-2:] + today[1] + today[2]

sys.path.append('../')
from class_device import device
from class_chip import chip

import aux_poly

def new_device(
        width=(30, 30),
        gap=(6, 12),
        length=(100, 50),
        a=10,
        b=6,
        layer='Nb_inv'):

    cap_1 = device()

    poly_1 = [1j*(length[0] + gap[0])]
    poly_1.append(poly_1[-1] - (width[0]/2 + gap[0]))
    poly_1.append(poly_1[-1] - 1j*length[0])
    poly_1.append(poly_1[-1] - width[1])
    poly_1.append(poly_1[-1] + 1j*(length[0] + length[1]))
    poly_1.append(1j*poly_1[-1].imag)

    poly_2 = [1j * length[0]]
    poly_2.append(poly_2[-1] - width[0]/2)
    poly_2.append(poly_2[-1] - 1j*length[0])
    poly_2.append(poly_2[-1] - (width[1] + gap[0] + gap[1]))
    poly_2.append(poly_2[-1] + 1j * (length[0] + length[1] + gap[0] + gap[1]))
    poly_2.append(-(a/2 + b) + 1j * poly_2[-1].imag)
    poly_2.append(poly_2[-1] - 1j*gap[1])
    poly_2.append(1j * poly_2[-1].imag)

    poly_3 = aux_poly.subtract(poly_2, poly_1)[0]
    poly_4 = aux_poly.reflect(poly_3, axis='y')
    cap_1.add_geometry(layer, [poly_3, poly_4])

    cap_1.add_port('inside', 1j * length[0])
    cap_1.add_port('outside', 1j*poly_1[-1].imag)

    return cap_1

x = new_device()

chip_1 = chip(name='cap',
              time=time_stamp,
              logo='QCD',
              die_size=(15e3, 15e3),
              chip_size=(10e3, 10e3),
              trap_size=(20, 100))
chip_1.combine_device(x, ref=5e3 * (1 + 1j), degree=0, axis='none', port='inside')
chip_1.gen_gds(marker=True, flux_trap=True, set_zero=True)
