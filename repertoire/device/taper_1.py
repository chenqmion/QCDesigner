import sys
import numpy as np

import datetime

today = str(datetime.date.today()).split('-')
time_stamp = today[0][-2:] + today[1] + today[2]

sys.path.append('../')
from class_device import device

from class_chip import chip
import aux_poly


def new_device(length=50,
               a=10, b=6,
               a2=5, b2=3,
               form='normal',
               layer='Nb_inv'):
    taper = device()

    poly_1 = []
    if form == 'normal':
        poly_1.append(1j * a / 2)
        poly_1.append(1j * (a / 2 + b))
        poly_1.append(length + 1j * (a2 / 2 + b2))
        poly_1.append(length + 1j * a2 / 2)
    elif form == 'elliptical':
        dy = (a2 / 2 + b2) - (a / 2 + b)

        if dy >= 0:
            s_c = 0 + 1j * (a2 / 2 + b2)
            phi_list = np.linspace(-np.pi / 2, 0, 36)[1:-1]
        else:
            s_c = length + 1j * (a / 2 + b)
            phi_list = np.linspace(-np.pi, -np.pi / 2, 36)[1:-1]

        dy2 = a2 / 2 - a / 2
        if dy2 >= 0:
            s_c2 = 0 + 1j * a2/2
            phi_list2 = np.linspace(-np.pi / 2, 0, 36)[1:-1]
        else:
            s_c2 = length + 1j * a / 2
            phi_list2 = np.linspace(-np.pi, -np.pi / 2, 36)[1:-1]

        poly_1.append(1j * a / 2)
        poly_1.append(1j * (a / 2 + b))

        poly_3 = []
        for num_phi, val_phi in enumerate(phi_list):
            poly_1.append(s_c + length * np.cos(val_phi) + 1j*np.abs(dy)*np.sin(val_phi))
            poly_3.append(s_c2 + length * np.cos(phi_list2[num_phi]) + 1j*np.abs(dy2)*np.sin(phi_list2[num_phi]))

        poly_1.append(length + 1j * (a2 / 2 + b2))
        poly_1.append(length + 1j * a2 / 2)
        poly_1 += poly_3[::-1]

    elif form == 'sigmoid':
        poly_1.append(1j * a / 2)
        poly_1.append(1j * (a / 2 + b))

        x_list = np.linspace(-10, 10, 101)
        dx = x_list[-1] - x_list[0]

        dy = (a2 / 2 + b2) - (a / 2 + b)
        dy2 = a2 / 2 - a/2

        x_list = x_list[1:-1]
        poly_3 = []
        for num_x, val_x in enumerate(x_list):
            poly_1.append(1j * (a / 2 + b) + (val_x - x_list[0])/dx * length + 1j*dy /(1+np.exp(-val_x)))
            poly_3.append(1j * a / 2 + (val_x - x_list[0])/dx * length + 1j * dy2 / (1 + np.exp(-val_x)))

        poly_1.append(length + 1j * (a2 / 2 + b2))
        poly_1.append(length + 1j * a2 / 2)
        poly_1 += poly_3[::-1]

    poly_2 = aux_poly.reflect(poly_1, axis='x', value=0)
    taper.add_geometry(layer, [poly_1, poly_2])

    taper.add_port('1', 0, degree=180)
    taper.add_port('2', length, degree=0)

    return taper

x = new_device(length=50, a=10, b=6, a2=15, b2=12, form='sigmoid')

chip_1 = chip(name='taper',
        time=time_stamp,
        logo='QCD',
        die_size=(15e3, 15e3),
        chip_size=(10e3, 10e3),
        trap_size = (20,100))

chip_1.combine_device(x, ref=5e3*(1+1j), degree=0, axis='none', port='1')

chip_1.gen_gds(marker=True, flux_trap=True, set_zero=True)
