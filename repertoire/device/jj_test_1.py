import sys

import numpy as np
import datetime

today = str(datetime.date.today()).split('-')
time_stamp = today[0][-2:] + today[1] + today[2]

sys.path.append('../')
from class_device import device
from class_chip import chip

import aux_poly
import jj_1 as JJ


# %% JJ test
def new_device(zone=(10, 10),
               contact_gap=0.5, protection_gap=1.5,
               nanowire_width=0.2, nanowire_extension=1,
               ghost = [0.2, 0.8],
               w_electrode=3):

    probe = device()

    poly_0 = [-300-300j]
    poly_0.append(poly_0[-1] + 1j * 600)
    poly_0.append(poly_0[-1] + 600)
    poly_0.append(poly_0[-1] - 1j * 600)

    poly_1 = [-250 - 250j]
    poly_1.append(poly_1[-1] + 500j)
    poly_1.append(poly_1[-1] + 500)
    poly_1.append(poly_1[-1] - 500j)

    poly_2 = [-50-250j]
    poly_2.append(poly_2[-1] + 1j * 100)
    poly_2.append(poly_2[-1] + 100)
    poly_2.append(poly_2[-1] - 1j * 100)

    poly_3 = [-250 - 50j]
    poly_3.append(poly_3[-1] + 1j * 100)
    poly_3.append(-zone[0]/2 + 1j * poly_3[-1].imag)
    poly_3.append(poly_3[-1] - 1j * 100)

    poly_1 = aux_poly.subtract(poly_1, poly_2)[0]
    poly_1 = aux_poly.subtract(poly_1, aux_poly.reflect(poly_2, axis='x', value=0))[0]

    poly_0 = aux_poly.subtract(poly_0, poly_1)[0]

    probe.add_geometry('Nb_inv', [poly_0, poly_3, aux_poly.reflect(poly_3, axis='y', value=0)], ref=0)

    JJ_1 = JJ.new_device(zone=zone,
               contact_gap=contact_gap, protection_gap=protection_gap,
               nanowire_width=nanowire_width, nanowire_extension=nanowire_extension,
               ghost = ghost,
               w_electrode=w_electrode)

    probe.combine_device(JJ_1, ref=-1j * zone[1]/2, port='270')

    probe.add_port('center', 0)

    return probe


# x = new_device()
#
# chip_1 = design(name='JJ_test',
#               time='250711',
#               logo='QCD',
#               die_size=(15e3, 15e3),
#               chip_size=(10e3, 10e3),
#               trap_size=(20, 100))
# chip_1.add_device('JJ_test', x, ref=5e3 * (1 + 1j), degree=0, axis='none', port='center')
# chip_1.gen_gds(marker=True, flux_trap=True, set_zero=True)
