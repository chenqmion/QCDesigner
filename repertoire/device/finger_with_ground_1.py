import sys

import numpy as np
import datetime

today = str(datetime.date.today()).split('-')
time_stamp = today[0][-2:] + today[1] + today[2]

sys.path.append('../')
from class_device import device
from class_chip import chip

import taper_1 as taper
import aux_poly

def new_device(finger_width=[15, 5],
               finger_gap=[5, 12],
               length=[100, 50],
               N=2,
               a=[10,10],
               b=[6,6],
               form='normal',
               layer='Nb_inv'):

    if finger_width[1] == 0:
        finger_gap[0] = finger_gap[0]/2

    width = (2 * N - 1) * finger_width[0] + 2 * (N - 1) * finger_width[1] + 4 * (N - 1) * finger_gap[0]
    length_finger = length[0] - finger_width[1] - 2 * finger_gap[0]

    cap_1 = device()

    taper_1 = taper.new_device(length=length[1], a=a[0], b=b[0], a2=width, b2=finger_gap[1], form=form, layer=layer)
    cap_1.combine_device(taper_1, ref=0, degree=0, axis='none', port='1')

    taper_2 = taper.new_device(length=length[1], a=a[1], b=b[1], a2=width, b2=finger_gap[1], form=form, layer=layer)
    cap_1.combine_device(taper_2, ref=length[1] + length[0], degree=0, axis='y', port='2')

    poly_1 = [0]
    poly_1.append(1j*(width + 2*finger_gap[1]))
    poly_1.append(poly_1[-1] + length[0])
    poly_1.append(poly_1[-1] - 1j*(width + 2*finger_gap[1]))

    if N == 1:
        poly_2 = [1j * finger_gap[1]]
        poly_2.append(poly_2[-1] + 1j * finger_width[0])
        poly_2.append(poly_2[-1] + length_finger/2)
        poly_2.append(poly_2[-1] - 1j * finger_width[0])

        poly_1 = aux_poly.subtract(poly_1, poly_2)[0]

        poly_3 = np.array(poly_2) + length_finger / 2 + finger_width[1] + 2*finger_gap[0]
        poly_1 = aux_poly.subtract(poly_1, poly_3)[0]

        poly_2 = [length_finger / 2 + finger_gap[0]]
        poly_2.append(poly_2[-1] + 1j * (width + 2 * finger_gap[1]))
        poly_2.append(poly_2[-1] + finger_width[1])
        poly_2.append(poly_2[-1] - 1j * (width + 2 * finger_gap[1]))

        poly_1 = aux_poly.subtract(poly_1, poly_2)

    else:
        poly_2 = [length_finger + finger_gap[0]]
        poly_2.append(poly_2[-1] + 1j*finger_gap[1])
        poly_2.append(poly_2[-1] + finger_width[1])
        poly_2.append(poly_2[-1] - 1j*finger_gap[1])

        poly_1 = aux_poly.subtract(poly_1, poly_2)[0]

        for num_1 in range(N):
            poly_2 = [1j*(finger_gap[1] + 2 * num_1 * (finger_width[0] + finger_width[1] + 2*finger_gap[0]))]
            poly_2.append(poly_2[-1] + 1j*finger_width[0])
            poly_2.append(poly_2[-1] + length_finger)
            poly_2.append(poly_2[-1] - 1j * finger_width[0])

            poly_1 = aux_poly.subtract(poly_1, poly_2)[0]

            if num_1 < (N-1):
                poly_3 = np.array(poly_2) + (2*finger_gap[0] + finger_width[1]) + 1j*(finger_width[0] + finger_width[1] + 2*finger_gap[0])
                poly_1 = aux_poly.subtract(poly_1, poly_3)[0]

                poly_3 = [poly_2[-1] + finger_gap[0]]
                poly_3.append(poly_3[-1] + 1j * (finger_width[0] + finger_gap[0]))
                poly_3.append(poly_3[-1] - length_finger)

                poly_3.append(poly_3[-1] + 1j * (finger_width[1] + finger_gap[0]))
                poly_3.append(poly_3[-1] + finger_width[1])
                poly_3.append(poly_3[-1] - 1j * (finger_gap[0]))

                poly_3.append(poly_3[-1] + length_finger)
                poly_3.append(poly_3[-1] - 1j * (finger_width[0] + finger_width[1] + finger_gap[0]))

                poly_1 = aux_poly.subtract(poly_1, poly_3)[0]

                poly_3b = aux_poly.reflect(poly_3, axis='y', value=length[0]/2)
                poly_3b = [pt + 1j*(finger_width[0] + finger_width[1] + 2*finger_gap[0]) for pt in poly_3b]
                poly_1 = aux_poly.subtract(poly_1, poly_3b)[0]
            else:
                poly_2 = [length_finger + finger_gap[0] + 1j*(width + 2*finger_gap[1])]
                poly_2.append(poly_2[-1] - 1j * (finger_width[0] + finger_gap[1]))
                poly_2.append(poly_2[-1] + finger_width[1])
                poly_2.append(poly_2[-1] + 1j * (finger_width[0] + finger_gap[1]))

                poly_1 = aux_poly.subtract(poly_1, poly_2)

    cap_1.add_geometry(layer, poly_1, ref=length[1] - 1j * (width / 2 + finger_gap[1]))

    cap_1.add_port('1', 0)
    cap_1.add_port('2', 2*length[1] + length[0])

    return cap_1

x = new_device()

chip_1 = chip(name='finger_with_ground',
              time=time_stamp,
              logo='QCD',
              die_size=(15e3, 15e3),
              chip_size=(10e3, 10e3),
              trap_size=(20, 100))

chip_1.add_device('finger_with_ground', x, ref=5e3 * (1 + 1j), degree=0, axis='none', port='1')
chip_1.gen_gds(marker=False, flux_trap=False, set_zero=True)
