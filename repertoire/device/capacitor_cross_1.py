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

#%% dependence
import cross_1 as cross

#%% design
def new_device(gnd_size=[300, 300],
               cap_size=[10, 10],
               protection_gap=10,
               a=[5, 10],
               b=[3, 6],
               layer='Nb_inv'):
    cap = device()

    # %%
    branch = cap_size[0] + a[0] / 2 + protection_gap

    cap_top = cross.new_device(angle=(0, 90, 270),
                               length=(branch, cap_size[1] / 2 + protection_gap, cap_size[1] / 2),
                               a_list=(cap_size[1], a[0], a[0]),
                               b_list=(protection_gap, b[0], b[0]),
                               c_list=(protection_gap, 0, protection_gap),
                               layer=layer)

    cap_top_ports = cap.combine_device(cap_top, ref=0, degree=0, axis='none', port='90')
    cap.ports['top'] = cap_top_ports['90']
    # cap.ports['top_'] = cap_top_ports['270'] + (branch + protection_gap - a/2 - b)/2
    cap.ports['top_'] = cap_top_ports['270'][0] + a[0] / 2 + (cap_size[0] + protection_gap) / 2

    # %%
    ald_width = np.max([gnd_size[0], cap_size[0]])

    cap_gnd = device()

    poly_1 = [-(ald_width + 2 * protection_gap) / 2]
    poly_1.append(poly_1[-1] - 1j * (gnd_size[1] + cap_size[1] + 3 * protection_gap))
    poly_1.append(poly_1[-1] + (ald_width + 2 * protection_gap))
    poly_1.append(poly_1[-1] + 1j * (gnd_size[1] + cap_size[1] + 3 * protection_gap))

    cap_gnd.add_geometry('SiO2', [poly_1], ref=1j * (cap_size[1] + 2 * protection_gap))
    # cap.ports['bottom_'] = cap.ports['top_'] + (branch + protection_gap - a/2 - b)/2 - 1j*gnd_size[1]
    cap.ports['bottom_'] = cap_top_ports['270'][0] - 1j * gnd_size[1]

    # if gnd_size[0] == 0:
    #     gnd_size[0] = gnd_size[1]

    poly_2 = [-gnd_size[0] / 2]
    poly_2.append(poly_2[-1] - 1j * gnd_size[1])
    poly_2.append(poly_2[-1] + gnd_size[0])
    poly_2.append(poly_2[-1] + 1j * gnd_size[1])

    poly_3 = [-cap_size[0] / 2]
    poly_3.append(poly_3[-1] + 1j * (cap_size[1] + protection_gap * 3 / 2))
    poly_3.append(poly_3[-1] + cap_size[0])
    poly_3.append(poly_3[-1] - 1j * (cap_size[1] + protection_gap * 3 / 2))

    poly_4 = [pt - 1j * (cap_size[1] + protection_gap * 3 / 2 + gnd_size[1]) for pt in poly_3]

    cap_gnd.add_geometry('Patch', [poly_2, poly_3, poly_4], ref=0)

    cap_gnd_ports = cap.combine_device(cap_gnd, ref=cap.ports['top_'], degree=0, axis='none')

    # %%
    cap_bottom = cross.new_device(angle=(0, 90, 270),
                                  length=(branch, cap_size[1] / 2 + protection_gap, cap_size[1] / 2),
                                  a_list=(cap_size[1], a[1], a[1]),
                                  b_list=(protection_gap, b[1], b[1]),
                                  c_list=(protection_gap, 0, protection_gap),
                                  layer=layer)

    cap_bottom_ports = cap.combine_device(cap_bottom, ref=cap.ports['bottom_'], degree=0, axis='x', port='270')
    cap.ports['bottom'] = cap_bottom_ports['90']

    return cap

#%% example
x = new_device(gnd_size=[0, 5])

chip_1 = chip(name=device_name,
              time=time_stamp,
              logo='QCD',
              die_size=(15e3, 15e3),
              chip_size=(10e3, 10e3),
              trap_size=(20, 100))
chip_1.combine_device(x, ref=5e3 * (1 + 1j), degree=0, axis='none', port='top')
chip_1.gen_gds(marker=True, flux_trap=True, set_zero=True)

# x0 = r - (a / 2 + b)
# x1 = r - a/2
# x2 = r + a/2
# x3 = r + (a / 2 + b)
#
# y0 = r - (cap_size[1] / 2 + protection_gap)
# y1 = r - cap_size[1] / 2
# y2 = r + cap_size[1] / 2
# y3 = r + (cap_size[1] / 2 + protection_gap)
#
# theta_list = np.arange(np.pi, np.pi*3/2, d_rad)
# if not(np.pi*3/2 in theta_list):
#     theta_list = np.append(theta_list, np.pi*3/2)
#
# path_1 = r + x0 * np.cos(theta_list) + 1j*y0 * np.sin(theta_list)
# path_2 = r + x1 * np.cos(theta_list) + 1j*y1 * np.sin(theta_list)
# path_3 = r + x2 * np.cos(theta_list) + 1j*y2 * np.sin(theta_list)
# path_4 = r + x3 * np.cos(theta_list) + 1j*y3 * np.sin(theta_list)
#
# poly_1 = list(path_1) + list(path_2[::-1])
# poly_2 = list(path_3) + list(path_4[::-1])
#
# cpw_top = device()
# cpw_top.add_geometry(layer, [poly_1, poly_2])

# cpw_top.add_port('1', 0)
