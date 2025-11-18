import datetime
import sys

import numpy as np

today = str(datetime.date.today()).split('-')
time_stamp = today[0][-2:] + today[1] + today[2]

sys.path.append('../')
from class_device import device

import aux_poly


# %% JJ
def new_device(zone=(24, 8),
               contact_gap=0.5, protection_gap=1.5,
               nanowire_width=0.2, nanowire_extension=1,
               ghost=[0.2, 0.8],
               w_electrode=3):
    nanowire_height = zone[1] / 2

    JJ = device()

    poly_0 = [-zone[0] / 2]
    poly_0.append(poly_0[-1] + 1j * zone[1])
    poly_0.append(poly_0[-1] + zone[0])
    poly_0.append(poly_0[-1] - 1j * zone[1])

    width_gap = protection_gap + nanowire_width + contact_gap
    height_1 = nanowire_height + nanowire_width / 2 + protection_gap

    poly_1 = [width_gap / 2 + 1j * height_1]
    poly_1.append(poly_1[-1].real + 1j * zone[1])
    poly_1.append(poly_1[-1] + w_electrode)
    poly_1.append(poly_1[-1].real + 1j * height_1)

    height_2 = nanowire_height - nanowire_width / 2 - contact_gap

    poly_2 = [-width_gap / 2]
    poly_2.append(poly_2[-1].real + 1j * height_2)
    poly_2.append(poly_2[-1] - w_electrode)
    poly_2.append(poly_2[-1].real - 1j * height_2)

    poly_3 = aux_poly.subtract(poly_0, poly_1)[0]
    poly_3 = aux_poly.subtract(poly_3, poly_2)[0]

    JJ.add_geometry('Nb_inv', [poly_3])
    JJ.add_port('270', 0)
    JJ.add_port('90', 1j * zone[1])

    JJ.add_port('0', zone[0] / 2 + 1j * zone[1] / 2)
    JJ.add_port('180', -zone[0] / 2 + 1j * zone[1] / 2)

    # JJ
    poly_1 = [-width_gap / 2 - nanowire_extension - 1j * nanowire_width / 2]
    poly_1.append(poly_1[-1] + 1j * nanowire_width)
    poly_1.append((width_gap / 2 - contact_gap + nanowire_extension) + 1j * poly_1[-1].imag)
    poly_1.append(poly_1[-1] - 1j * nanowire_width)
    poly_1 = np.array(poly_1) + 1j * nanowire_height

    JJ.add_geometry('JJ1', [poly_1])

    poly_2 = [-nanowire_width / 2 + 1j * (nanowire_height - nanowire_width / 2 - nanowire_extension)]
    poly_2.append(poly_2[-1].real + 1j * (height_1 + nanowire_extension))
    poly_2.append(poly_2[-1] + nanowire_width)
    poly_2.append(poly_2[-1].real + 1j * (nanowire_height - nanowire_width / 2 - nanowire_extension))
    poly_2 = np.array(poly_2) + width_gap / 2 - contact_gap - nanowire_width / 2

    JJ.add_geometry('JJ1', [poly_2])

    # ghost
    poly_1_ghost = [- ghost[0] - 1j * (nanowire_width + ghost[0]) / 2]
    poly_1_ghost.append(poly_1_ghost[-1] + 1j * (nanowire_width + ghost[0]))
    poly_1_ghost.append(poly_1_ghost[-1] + ghost[0] + ghost[1])
    poly_1_ghost.append(poly_1_ghost[-1] - 1j * (nanowire_width + ghost[0]))

    ref_1 = (width_gap / 2 - contact_gap + nanowire_extension) + 1j * nanowire_height
    ref_2 = -width_gap / 2 - nanowire_extension + 1j * nanowire_height

    JJ.add_geometry('Ghost1', [poly_1_ghost],
                    ref=ref_1)
    JJ.add_geometry('Ghost1', [aux_poly.rotate(poly_1_ghost, degree=180)],
                    ref=ref_2)

    ref_3 = width_gap / 2 - contact_gap - nanowire_width / 2 + 1j * (height_1 + nanowire_extension)
    ref_4 = width_gap / 2 - contact_gap - nanowire_width / 2 + 1j * (
                nanowire_height - nanowire_width / 2 - nanowire_extension)

    JJ.add_geometry('Ghost1', [aux_poly.rotate(poly_1_ghost, degree=90)],
                    ref=ref_3)
    JJ.add_geometry('Ghost1', [aux_poly.rotate(poly_1_ghost, degree=270)],
                    ref=ref_4)

    # patch
    overlap = nanowire_extension + contact_gap

    poly_1_patch = [ref_2.real - contact_gap + 1j * (height_2 - overlap)]
    poly_1_patch.append(ref_2 - contact_gap + 1j * (nanowire_width / 2 + contact_gap))
    poly_1_patch.append(poly_1_patch[-1] + overlap)
    poly_1_patch.append(poly_1_patch[-1].real + 1j * (height_2 - overlap))

    JJ.add_geometry('Patch', [poly_1_patch])

    height_1 = nanowire_height + nanowire_width / 2 + protection_gap

    poly_2_patch = [ref_3 - (nanowire_width / 2 + contact_gap) + 1j * contact_gap]
    poly_2_patch.append((width_gap / 2 + overlap) + 1j * poly_2_patch[-1].imag)
    poly_2_patch.append(poly_2_patch[-1] - 1j * overlap)
    poly_2_patch.append(ref_3.real - (nanowire_width / 2 + contact_gap) + 1j * poly_2_patch[-1].imag)

    JJ.add_geometry('Patch', [poly_2_patch])

    return JJ

# x = new_device()
#
# chip_1 = design(name='JJ',
#               time='250611',
#               logo='QCD',
#               die_size=(15e3, 15e3),
#               chip_size=(10e3, 10e3),
#               trap_size=(20, 100))
# chip_1.add_device('JJ', x, ref=5e3 * (1 + 1j), degree=0, axis='none', port='270')
# chip_1.gen_gds(marker=True, flux_trap=True, set_zero=True)
