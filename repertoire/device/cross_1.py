import sys

import numpy as np
import datetime

today = str(datetime.date.today()).split('-')
time_stamp = today[0][-2:] + today[1] + today[2]

sys.path.append('../')
from class_device import device
from class_chip import chip

import aux_poly


def new_device(angle=(0, 90, 180, 270),
              length=(130, 130, 130, 130),
              a_list=(8, 8, 8, 8),
              b_list=(8, 8, 8, 8),
              c_list=(8, 8, 8, 8),
              layer='Nb_inv'):
    cross = device()

    idx_angle = np.argsort(angle)
    angle = np.array(angle)[idx_angle]
    length = np.array(length)[idx_angle]
    a_list = np.array(a_list)[idx_angle]
    b_list = np.array(b_list)[idx_angle]
    c_list = np.array(c_list)[idx_angle]

    path_inner = []
    path_outer = []
    for num_angle, val_angle in enumerate(angle):
        num_angle2 = (num_angle + 1) % len(angle)

        for num_1 in range(2):
            x0 = (length[num_angle] + num_1 * c_list[num_angle]) * np.exp(1j * angle[num_angle] * np.pi / 180)
            y01 = (a_list[num_angle] / 2 + num_1 * b_list[num_angle]) * np.exp(
                1j * (angle[num_angle] + 90) * np.pi / 180)
            y02 = x0 + y01

            if num_1 == 1:
                cross.add_port(str(angle[num_angle]), x0)

            x1 = (length[num_angle2] + num_1 * c_list[num_angle2]) * np.exp(1j * angle[num_angle2] * np.pi / 180)
            y11 = (a_list[num_angle2] / 2 + num_1 * b_list[num_angle2]) * np.exp(
                1j * (angle[num_angle2] - 90) * np.pi / 180)
            y12 = x1 + y11

            # find intersect
            a0 = (y01 - y02).imag
            b0 = (y02 - y01).real
            c0 = y01.real * y02.imag - y02.real * y01.imag

            a1 = (y11 - y12).imag
            b1 = (y12 - y11).real
            c1 = y11.real * y12.imag - y12.real * y11.imag
            d = a0 * b1 - a1 * b0

            if d > 1e-2:
                xc = (b0 * c1 - b1 * c0) / d
                yc = (a1 * c0 - a0 * c1) / d

                if num_1 == 0:
                    path_inner += [y02, xc + 1j * yc, y12]
                else:
                    path_outer += [y02, xc + 1j * yc, y12]
            else:
                _angle = (angle[num_angle] + angle[(num_angle + 1) % len(angle)]) / 2
                y01 = (a_list[num_angle] / 2 + num_1 * b_list[num_angle]) * np.exp(
                    1j * _angle * np.pi / 180)
                y02 = x0 + y01

                _angle2 = (angle[num_angle2] + angle[(num_angle2 - 1) % len(angle)]) / 2
                y11 = (a_list[num_angle2] / 2 + num_1 * b_list[num_angle2]) * np.exp(
                    1j * _angle2 * np.pi / 180)
                y12 = x1 + y11

                if num_1 == 0:
                    path_inner += [y02, y01, y11, y12]
                else:
                    path_outer += [y02, y01, y11, y12]

    geometry_1 = aux_poly.subtract(path_outer, path_inner)
    cross.add_geometry(layer, geometry_1)

    return cross

x = new_device(angle=(0, 180, 270),
              length=(100, 100, 100),
              a_list=(5, 10, 5),
              b_list=(5, 6, 5),
              c_list=(0, 0, 0),
              layer='Nb_inv')

# x = new_device(angle=(0, 180, 270),
#               length=(130, 130, 130),
#               a_list=(5, 10, 5),
#               b_list=(5, 6, 5),
#               c_list=(0, 0, 0),
#               layer='Nb_inv')

# chip_1 = design(name='cross',
#               time='250611',
#               logo='QCD',
#               die_size=(15e3, 15e3),
#               chip_size=(10e3, 10e3),
#               trap_size=(20, 100))
# chip_1.add_device('cross', x, ref=5e3 * (1 + 1j), degree=0, axis='none', port='0')
# chip_1.gen_gds(marker=True, flux_trap=True, set_zero=True)

# x = cap()
#
# chip_1 = design(name='cross_cap',
#               time='250611',
#               logo='QCD',
#               die_size=(15e3, 15e3),
#               chip_size=(10e3, 10e3),
#               trap_size=(20, 100))
# chip_1.add_device('cross_cap', x, ref=5e3 * (1 + 1j), degree=0, axis='none', port='inside')
# chip_1.gen_gds(marker=True, flux_trap=True, set_zero=True)
