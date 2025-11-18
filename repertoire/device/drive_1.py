import datetime
import sys

today = str(datetime.date.today()).split('-')
time_stamp = today[0][-2:] + today[1] + today[2]

sys.path.append('../')
from class_device import device

import cpw_1 as cpw
import taper_1 as taper


def new_device(length=[10, 50],
               a=10, b=6, a2=3, b2=2, layer='Nv_inv'):
    xy = device()
    taper_1 = taper.new_device(length=length[0], a=a, b=b, a2=a2, b2=b2, layer=layer)
    taper_ports = xy.combine_device(taper_1, ref=0, port='1')

    cpw1 = cpw.cpw_straight(taper_ports['2'], taper_ports['2'] + length[1], a=a2, b=b2)
    xy.add_geometry(layer, cpw1)

    poly_1 = [-b2 - 1j * (a2 / 2)]
    poly_1.append(poly_1[-1] + 1j * a2)
    poly_1.append(poly_1[-1] + b2)
    poly_1.append(poly_1[-1] - 1j * a2)

    xy.add_geometry(layer, [poly_1], ref=taper_ports['2'] + length[1])

    xy.add_port('input', 0)
    xy.add_port('output', length[0] + length[1])

    return xy

# x = new_device()
# chip_1 = design(name='drive',
#               time='250611',
#               logo='QCD',
#               die_size=(15e3, 15e3),
#               chip_size=(10e3, 10e3),
#               trap_size=(20, 100))
# chip_1.add_device('drive', x, ref=5e3 * (1 + 1j), degree=0, axis='none', port='input')
# chip_1.gen_gds(marker=True, flux_trap=True, set_zero=True)
