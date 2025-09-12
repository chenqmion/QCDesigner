import sys

sys.path.append('../')
from class_device import device

import aux_poly

import taper_1 as taper

def new_device(pad=400,
               gap=240,
               taper_length=400,
               a=10, b=6, layer='Nb_inv'):
    launcher_1 = device()
    b2 = (b / a) * pad

    poly_1 = [0]
    poly_1.append(1j * (pad + 2 * b2) / 2)
    poly_1.append(pad + gap + 1j * (pad + 2 * b2) / 2)
    poly_1.append(pad + gap + 1j * pad / 2)
    poly_1.append(gap + 1j * pad / 2)
    poly_1.append(gap)

    poly_2 = aux_poly.reflect(poly_1, axis='x', value=0)
    launcher_1.add_geometry(layer, [poly_1, poly_2])

    taper_1 = taper.new_device(length=taper_length, a=pad, b=b2, a2=a, b2=b)
    new_ports = launcher_1.combine_device(taper_1, ref=pad + gap, degree=0, port='1')

    launcher_1.add_port('1', 0, degree=180)
    launcher_1.add_port('2', new_ports['2'][0], degree=0)

    return launcher_1

# x = new_device(pad=400,
#                  gap=240,
#                  taper_length=400,
#                  a=10, b=6, layer='Nb_inv')
#
# chip_1 = design(name='launcher',
#         time='250611',
#         logo='QCD',
#         die_size=(15e3, 15e3),
#         chip_size=(10e3, 10e3),
#         trap_size = (20,100))
# chip_1.add_device('launcher', x, ref=5e3*(1+1j), degree=0, axis='none', port='1')
# chip_1.gen_gds(marker=True, flux_trap=True, set_zero=True)
