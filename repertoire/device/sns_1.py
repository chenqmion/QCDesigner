import numpy as np
import scipy as sci

import datetime
import sys
import os

today = str(datetime.date.today()).split('-')
time_stamp = today[0][-2:] + today[1] + today[2]
device_name = os.path.basename(__file__)[:-3]

sys.path.append('../')
from class_device import device
from class_chip import chip
import aux_poly

#%% design
def new_device(zone=(22, 10),
               island_width=[0.3, 0.3, 0.3],
               island_gap=[0.3, 0.3],
               with_absorber=False,
               contact_gap=0.5, protection_gap=1.5,
               nanowire_width=0.1,
               nanowire_extension=1,
               x_shift=0,
               ghost=[0.2, 0.8],
               w_electrode=3):
    nanowire_length = np.sum(island_width) + np.sum(island_gap) - island_width[0] / 2 - island_width[-1] / 2
    ref_island = zone[1] / 2 + nanowire_length / 2

    JJ = device()

    poly_0 = [-zone[0] / 2]
    poly_0.append(poly_0[-1] + 1j * zone[1])
    poly_0.append(poly_0[-1] + zone[0])
    poly_0.append(poly_0[-1] - 1j * zone[1])

    width_gap = nanowire_width + 2 * (nanowire_extension + ghost[1] + protection_gap)

    height_1 = ref_island + island_width[0] / 2 + contact_gap

    poly_1 = [width_gap / 2 + 1j * height_1]
    poly_1.append(poly_1[-1].real + 1j * zone[1])
    poly_1.append(poly_1[-1] + w_electrode)
    poly_1.append(poly_1[-1].real + 1j * height_1)

    poly_1 = [poly_ + x_shift for poly_ in poly_1]

    height_2 = (ref_island - nanowire_length) - island_width[-1] / 2 - contact_gap
    if not (with_absorber):
        poly_2 = [-width_gap / 2]
        poly_2.append(poly_2[-1].real + 1j * height_2)
        poly_2.append(poly_2[-1] - w_electrode)
        poly_2.append(poly_2[-1].real - 1j * height_2)
    else:
        poly_2 = [width_gap / 2]
        poly_2.append(poly_2[-1] + 1j * height_2)
        poly_2.append(poly_2[-1] + w_electrode)
        poly_2.append(poly_2[-1] - 1j * height_2)

    poly_2 = [poly_ + x_shift for poly_ in poly_2]

    poly_3 = aux_poly.subtract(poly_0, poly_1)[0]
    poly_3 = aux_poly.subtract(poly_3, poly_2)[0]

    if with_absorber:
        # height_4 = (ref_island - island_width[0]/2 - island_gap[0]) + contact_gap
        # poly_4 = [-zone[0] / 2 + 1j * height_4]
        # poly_4.append(poly_4[-1] + 1j * w_electrode)
        # poly_4.append(1j*poly_4[-1].imag - width_gap / 2)
        # poly_4.append(poly_4[-1].real + 1j * height_4)

        height_4 = (ref_island - island_width[0] / 2 - island_gap[0]) - island_width[1] - contact_gap - w_electrode
        poly_4 = [-zone[0] / 2 + 1j * height_4]
        poly_4.append(poly_4[-1] + 1j * w_electrode)
        poly_4.append(1j * poly_4[-1].imag - width_gap / 2)
        poly_4.append(poly_4[-1].real + 1j * height_4)

        poly_4 = [poly_ + x_shift for poly_ in poly_4]

        poly_3 = aux_poly.subtract(poly_3, poly_4)[0]

    JJ.add_geometry('Nb_inv', [poly_3])
    JJ.add_port('270', 0)
    JJ.add_port('90', 1j * zone[1])

    JJ.add_port('0', zone[0] / 2 + 1j * zone[1] / 2)
    JJ.add_port('180', -zone[0] / 2 + 1j * zone[1] / 2)

    # JJ
    ref_list = []
    for num_ in range(len(island_width)):
        ref_ = []
        if (with_absorber and (num_ == 1)) or (not (with_absorber) and (num_ == len(island_width) - 1)):
            poly_1 = [-width_gap / 2 - nanowire_extension - 1j * island_width[num_] / 2]
            ref_.append(-width_gap / 2 - nanowire_extension + 1j * ref_island)
        else:
            poly_1 = [- nanowire_extension - nanowire_width / 2 - 1j * island_width[num_] / 2]
            ref_.append(- nanowire_extension - nanowire_width / 2 + 1j * ref_island)

        poly_1.append(poly_1[-1] + 1j * island_width[num_])

        if (num_ == 0):
            if with_absorber:
                poly_1.append(width_gap / 2 + w_electrode - contact_gap + 1j * poly_1[-1].imag)
                ref_.append(width_gap / 2 + w_electrode - contact_gap + 1j * ref_island)
            else:
                poly_1.append(width_gap / 2 + nanowire_extension + 1j * poly_1[-1].imag)
                ref_.append(width_gap / 2 + nanowire_extension + 1j * ref_island)
        elif ((num_ == len(island_width) - 1) and with_absorber):
            poly_1.append(width_gap / 2 + nanowire_extension + 1j * poly_1[-1].imag)
            ref_.append(width_gap / 2 + nanowire_extension + 1j * ref_island)
        else:
            poly_1.append(nanowire_width / 2 + nanowire_extension + 1j * poly_1[-1].imag)
            ref_.append(nanowire_width / 2 + nanowire_extension + 1j * ref_island)

        poly_1.append(poly_1[-1] - 1j * island_width[num_])
        JJ.add_geometry('JJ1', [poly_1], ref=x_shift + 1j * ref_island)

        ref_list.append(ref_)
        if num_ < (len(island_width) - 1):
            ref_island += -island_gap[num_] - island_width[num_] / 2 - island_width[num_ + 1] / 2

    poly_2 = [-nanowire_width / 2 + 1j * (ref_list[-1][0].imag - island_width[-1] / 2 - nanowire_extension)]
    poly_2.append(poly_2[-1].real + 1j * (ref_list[0][0].imag + island_width[0] / 2 + nanowire_extension))
    poly_2.append(poly_2[-1] + nanowire_width)
    poly_2.append(poly_2[-1].real + 1j * (ref_list[-1][0].imag - island_width[-1] / 2 - nanowire_extension))
    JJ.add_geometry('JJ1', [poly_2], ref=x_shift)

    # ghost
    for num_ in range(len(island_width)):
        poly_1_ghost = [- ghost[0] - 1j * (island_width[num_] + ghost[0]) / 2]
        poly_1_ghost.append(poly_1_ghost[-1] + 1j * (island_width[num_] + ghost[0]))
        poly_1_ghost.append(poly_1_ghost[-1] + ghost[0] + ghost[1])
        poly_1_ghost.append(poly_1_ghost[-1] - 1j * (island_width[num_] + ghost[0]))

        ref_2, ref_1 = ref_list[num_]

        JJ.add_geometry('Ghost1', [poly_1_ghost],
                        ref=x_shift + ref_1)
        JJ.add_geometry('Ghost1', [aux_poly.rotate(poly_1_ghost, degree=180)],
                        ref=x_shift + ref_2)

    poly_1_ghost = [- ghost[0] - 1j * (nanowire_width + ghost[0]) / 2]
    poly_1_ghost.append(poly_1_ghost[-1] + 1j * (nanowire_width + ghost[0]))
    poly_1_ghost.append(poly_1_ghost[-1] + ghost[0] + ghost[1])
    poly_1_ghost.append(poly_1_ghost[-1] - 1j * (nanowire_width + ghost[0]))

    ref_3 = 1j * (ref_list[0][0].imag + island_width[0] / 2 + nanowire_extension)
    ref_4 = 1j * (ref_list[-1][0].imag - island_width[-1] / 2 - nanowire_extension)

    JJ.add_geometry('Ghost1', [aux_poly.rotate(poly_1_ghost, degree=90)],
                    ref=x_shift + ref_3)
    JJ.add_geometry('Ghost1', [aux_poly.rotate(poly_1_ghost, degree=270)],
                    ref=x_shift + ref_4)

    # patch
    overlap = nanowire_extension + contact_gap

    if not (with_absorber):
        poly_1_patch = [ref_list[-1][0].real - contact_gap + 1j * (height_2 - overlap)]
        poly_1_patch.append(ref_list[-1][0] - contact_gap + 1j * (island_width[-1] / 2 + contact_gap))
        poly_1_patch.append(poly_1_patch[-1] + overlap)
        poly_1_patch.append(poly_1_patch[-1].real + 1j * (height_2 - overlap))
    else:
        poly_1_patch = [ref_list[-1][1].real + contact_gap + 1j * (height_2 - overlap)]
        poly_1_patch.append(ref_list[-1][1] + contact_gap + 1j * (island_width[-1] / 2 + contact_gap))
        poly_1_patch.append(poly_1_patch[-1] - overlap)
        poly_1_patch.append(poly_1_patch[-1].real + 1j * (height_2 - overlap))

    JJ.add_geometry('Patch', [poly_1_patch], ref=x_shift)

    poly_2_patch = [ref_list[0][1].real + contact_gap + 1j * (height_1 + overlap)]
    poly_2_patch.append(ref_list[0][1] + contact_gap - 1j * (island_width[0] / 2 + contact_gap))
    poly_2_patch.append(poly_2_patch[-1] - overlap)
    poly_2_patch.append(poly_2_patch[-1].real + 1j * (height_1 + overlap))

    JJ.add_geometry('Patch', [poly_2_patch], ref=x_shift)

    if with_absorber:
        # poly_3_patch = [ref_list[1][0].real - contact_gap + 1j * (height_4 + overlap)]
        # poly_3_patch.append(ref_list[1][0] - contact_gap - 1j * (island_width[0] / 2 + contact_gap))
        # poly_3_patch.append(poly_3_patch[-1] + overlap)
        # poly_3_patch.append(poly_3_patch[-1].real + 1j * (height_4 + overlap))

        poly_3_patch = [ref_list[1][0].real - contact_gap + 1j * (height_4 + overlap)]
        poly_3_patch.append(ref_list[1][0] - contact_gap + 1j * (island_width[0] / 2 + contact_gap))
        poly_3_patch.append(poly_3_patch[-1] + overlap)
        poly_3_patch.append(poly_3_patch[-1].real + 1j * (height_4 + overlap))

        JJ.add_geometry('Patch', [poly_3_patch], ref=x_shift)

    return JJ

#%% example
x = new_device(with_absorber=True)

chip_1 = chip(name=device_name,
              time=time_stamp,
              logo='QCD',
              die_size=(15e3, 15e3),
              chip_size=(10e3, 10e3),
              trap_size=(20, 100))
chip_1.combine_device(x, ref=5e3 * (1 + 1j), degree=0, axis='none', port='270')
chip_1.gen_gds(marker=True, flux_trap=True, set_zero=True)
