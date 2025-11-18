import datetime
import sys

import numpy as np

today = str(datetime.date.today()).split('-')
time_stamp = today[0][-2:] + today[1] + today[2]

sys.path.append('../')
from class_device import device
from class_chip import chip

import aux_poly


# %% JJ
def new_device(zone=(10, 10), squid_height=2, squid_width=6,
               contact_gap=0.5, protection_gap=1.5,
               nanowire_width=0.2, nanowire_extension=1,
               ghost=[0.2, 0.8],
               w_electrode=3):
    nanowire_height = zone[1] / 2 + squid_height / 2 - (nanowire_width / 2 + contact_gap) / 2

    SQUID = device()

    poly_0 = [-zone[0] / 2]
    poly_0.append(poly_0[-1] + 1j * zone[1])
    poly_0.append(poly_0[-1] + zone[0])
    poly_0.append(poly_0[-1] - 1j * zone[1])

    width_1 = w_electrode
    height_1 = nanowire_height + nanowire_width / 2 + contact_gap

    poly_1 = [-width_1 / 2 + 1j * height_1]
    poly_1.append(-width_1 / 2 + 1j * zone[1])
    poly_1.append(width_1 / 2 + 1j * zone[1])
    poly_1.append(width_1 / 2 + 1j * height_1)

    width_2 = squid_width - nanowire_width - 2 * contact_gap
    height_2 = nanowire_height - squid_height

    poly_2 = [-width_2 / 2]
    poly_2.append(poly_2[-1].real + 1j * height_2)
    poly_2.append(poly_2[-1] + width_2)
    poly_2.append(poly_2[-1].real - 1j * height_2)

    poly_4 = aux_poly.subtract(poly_0, poly_1)[0]
    poly_4 = aux_poly.subtract(poly_4, poly_2)[0]

    SQUID.add_geometry('Nb_inv', [poly_4])
    SQUID.add_port('270', 0)
    SQUID.add_port('90', 1j * zone[1])

    SQUID.add_port('0', zone[0] / 2 + 1j * zone[1] / 2)
    SQUID.add_port('180', -zone[0] / 2 + 1j * zone[1] / 2)

    # JJ
    poly_1 = [-(squid_width / 2 + nanowire_width / 2 + nanowire_extension) - 1j * nanowire_width / 2]
    poly_1.append(poly_1[-1] + 1j * nanowire_width)
    poly_1.append((squid_width / 2 + nanowire_width / 2 + nanowire_extension) + 1j * poly_1[-1].imag)
    poly_1.append(poly_1[-1] - 1j * nanowire_width)
    poly_1 = np.array(poly_1) + 1j * nanowire_height

    SQUID.add_geometry('JJ1', [poly_1])

    poly_2 = [-nanowire_width / 2 + 1j * (height_2 - nanowire_extension)]
    poly_2.append(poly_2[-1].real + 1j * (height_1 + nanowire_extension))
    poly_2.append(poly_2[-1] + nanowire_width)
    poly_2.append(poly_2[-1].real + 1j * (height_2 - nanowire_extension))
    poly_2 = np.array(poly_2) - squid_width / 2

    poly_22 = aux_poly.reflect(poly_2, axis='y', value=0)
    SQUID.add_geometry('JJ1', [poly_2, poly_22])

    # ghost
    poly_1_ghost = [- ghost[0] - 1j * (nanowire_width + ghost[0]) / 2]
    poly_1_ghost.append(poly_1_ghost[-1] + 1j * (nanowire_width + ghost[0]))
    poly_1_ghost.append(poly_1_ghost[-1] + ghost[0] + ghost[1])
    poly_1_ghost.append(poly_1_ghost[-1] - 1j * (nanowire_width + ghost[0]))

    ref_1 = (squid_width / 2 + nanowire_width / 2 + nanowire_extension) + 1j * nanowire_height
    ref_2 = -(squid_width / 2 + nanowire_width / 2 + nanowire_extension) + 1j * nanowire_height

    SQUID.add_geometry('Ghost1', [poly_1_ghost],
                       ref=ref_1)
    SQUID.add_geometry('Ghost1', [aux_poly.rotate(poly_1_ghost, degree=180)],
                       ref=ref_2)

    ref_3 = squid_width / 2 + 1j * (height_1 + nanowire_extension)
    ref_4 = -squid_width / 2 + 1j * (height_1 + nanowire_extension)

    SQUID.add_geometry('Ghost1', [aux_poly.rotate(poly_1_ghost, degree=90)],
                       ref=ref_3)
    SQUID.add_geometry('Ghost1', [aux_poly.rotate(poly_1_ghost, degree=90)],
                       ref=ref_4)

    ref_5 = squid_width / 2 + 1j * (height_2 - nanowire_extension)
    ref_6 = -squid_width / 2 + 1j * (height_2 - nanowire_extension)

    SQUID.add_geometry('Ghost1', [aux_poly.rotate(poly_1_ghost, degree=270)],
                       ref=ref_5)
    SQUID.add_geometry('Ghost1', [aux_poly.rotate(poly_1_ghost, degree=270)],
                       ref=ref_6)

    # patch
    overlap = nanowire_extension + contact_gap

    poly_1_patch = [-overlap / 2 + 1j * (height_1 + overlap)]
    poly_1_patch.append(poly_1_patch[-1].real + 1j * (nanowire_height - nanowire_width / 2 - contact_gap))
    poly_1_patch.append(poly_1_patch[-1] + overlap)
    poly_1_patch.append(poly_1_patch[-1].real + 1j * (height_1 + overlap))

    SQUID.add_geometry('Patch', [poly_1_patch])

    poly_2_patch = [- (squid_width / 2 + nanowire_width / 2 + contact_gap) + 1j * (height_2 - overlap)]
    poly_2_patch.append(1j * poly_2_patch[-1].imag + (-width_2 / 2 + overlap))
    poly_2_patch.append(poly_2_patch[-1] + 1j * overlap)
    poly_2_patch.append(1j * poly_2_patch[-1].imag - (squid_width / 2 + nanowire_width / 2 + contact_gap))

    SQUID.add_geometry('Patch', [poly_2_patch, aux_poly.reflect(poly_2_patch, axis='y')])

    return SQUID


x = new_device()

chip_1 = chip(name='SQUID',
              time=time_stamp,
              logo='QCD',
              die_size=(15e3, 15e3),
              chip_size=(10e3, 10e3),
              trap_size=(20, 100))
chip_1.add_device('SQUID', x, ref=5e3 * (1 + 1j), degree=0, axis='none', port='270')
chip_1.gen_gds(marker=True, flux_trap=True, set_zero=True)
