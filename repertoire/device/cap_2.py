import datetime
import sys

today = str(datetime.date.today()).split('-')
time_stamp = today[0][-2:] + today[1] + today[2]

sys.path.append('../')
from class_device import device
from class_chip import chip

import aux_poly


def new_device(
        width=(40, 30, 3),
        gap=(6, 12),
        length=(100, 50),
        a=10,
        b=6,
        layer='Nb_inv'):
    cap_1 = device()

    # %% outer
    poly_1 = [1j * (length[0] + 2 * gap[0])]
    poly_1.append(poly_1[-1] - (width[0] / 2 + 2 * gap[0] + width[2]))
    poly_1.append(poly_1[-1] - 1j * (length[0] + gap[0]))
    poly_1.append(poly_1[-1] - width[1])
    poly_1.append(poly_1[-1] + 1j * (length[0] + length[1] + gap[0]))
    poly_1.append(1j * poly_1[-1].imag)

    poly_2 = [1j * (length[0] + gap[0])]
    poly_2.append(poly_2[-1] - (width[0] / 2 + gap[0] + width[2]))
    poly_2.append(poly_2[-1] - 1j * (length[0] + gap[0]))
    poly_2.append(poly_2[-1] - (width[1] + gap[0] + gap[1]))
    poly_2.append(poly_2[-1] + 1j * (length[0] + length[1] + 2 * gap[0] + gap[1]))
    poly_2.append(-(a / 2 + b) + 1j * poly_2[-1].imag)
    poly_2.append(poly_2[-1] - 1j * gap[1])
    poly_2.append(1j * poly_2[-1].imag)

    poly_3 = aux_poly.subtract(poly_2, poly_1)[0]
    poly_4 = aux_poly.reflect(poly_3, axis='y')
    cap_1.add_geometry(layer, [poly_3, poly_4])

    cap_1.add_port('outside', 1j * poly_1[-1].imag)

    # %% inner
    poly_1 = [-width[0] / 2 - gap[0]]
    poly_1.append(poly_1[-1] + 1j * (length[0] + gap[0]))
    poly_1.append(poly_1[-1] + (width[0] + 2 * gap[0]))
    poly_1.append(poly_1[-1] - 1j * (length[0] + gap[0]))

    poly_2 = [-width[0] / 2]
    poly_2.append(poly_2[-1] + 1j * length[0])
    poly_2.append(poly_2[-1] + width[0])
    poly_2.append(poly_2[-1] - 1j * length[0])

    poly_3 = aux_poly.subtract(poly_1, poly_2)[0]
    cap_1.add_geometry(layer, [poly_3], ref=-1j * width[2])

    cap_1.add_port('inside', 0)

    return cap_1


x = new_device()

chip_1 = chip(name='cap',
              time=time_stamp,
              logo='QCD',
              die_size=(15e3, 15e3),
              chip_size=(10e3, 10e3),
              trap_size=(20, 100))

chip_1.add_device('cap', x, ref=5e3 * (1 + 1j), degree=0, axis='none', port='inside')
chip_1.gen_gds(marker=False, flux_trap=False, set_zero=True)
