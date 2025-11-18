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
import aux_marker

#%% dependence
import launcher_1 as launcher

#%% design
def new_device(name=device_name,
               time=time_stamp,
               logo='QCD',
               die_size=(15e3, 15e3),
               chip_size=(10e3, 10e3),
               trap_size=(20, 100),
               # launcher
               launchers=['launcher_--', 'launcher_0-', 'launcher_-+', 'launcher_-0', 'launcher_++', 'launcher_0+',
                          'launcher_+-', 'launcher_+0'],
               pad=400,
               gap=240,
               taper_length=400,
               gnd_slot=350,
               # general
               a=10, b=6
               ):
    chip_1 = chip(name=name, time=time, logo=logo,
                  die_size=die_size, chip_size=chip_size, trap_size=trap_size)

    # %% base
    poly_1 = []
    poly_1.append(0)
    poly_1.append(1j * chip_size[1])
    poly_1.append(chip_size[0] + 1j * chip_size[1])
    poly_1.append(chip_size[0])

    poly_2 = []
    poly_2.append(0)
    poly_2.append(1j * die_size[1])
    poly_2.append(die_size[0] + 1j * die_size[1])
    poly_2.append(die_size[0])
    poly_2 = np.array(poly_2) + (chip_size[0] - die_size[0]) / 2 + 1j * (
            chip_size[1] - die_size[1]) / 2

    poly_1 = np.squeeze(aux_poly.subtract(poly_2, poly_1))

    # %% decorator
    geomrtey_2 = aux_marker.decorator(die_size=die_size,
                                      chip_size=chip_size)
    for poly_2 in geomrtey_2:
        poly_1 = np.squeeze(aux_poly.subtract(poly_1, poly_2))

    chip_1.add_geometry('remarks', [poly_1])

    # %% notes
    # position_list = [chip_size[0]/3 + 0.4e3 * 1j,
    #                  chip_size[0]/3 + 1j*(chip_size[1] - 0.4e3),
    #                  chip_size[0]*2/3 + 1j*(chip_size[1] - 0.4e3)]
    #
    # geometry_name = aux_marker.text(name, size=2e2)
    # chip_1.add_geometry('remarks', geometry_name, ref=position_list[2])
    #
    # geometry_time = aux_marker.text(time, size=2e2)
    # chip_1.add_geometry('remarks', geometry_time, ref=position_list[1])
    #
    # geometry_logo = aux_marker.text(logo, size=2e2)
    # chip_1.add_geometry('remarks', geometry_logo, ref=position_list[0])

    # %% launcher
    poly_2 = [0, 2j * gnd_slot, 2 * gnd_slot]
    position_2 = [0, 1j * chip_size[1], (chip_size[0] + 1j * chip_size[1]), chip_size[0]]
    for num_2 in range(4):
        chip_1.add_geometry('remarks', [poly_2], ref=position_2[num_2], degree=-90 * num_2,
                            axis='none', ref_port=0)

    launcher_1 = launcher.new_device(pad=pad,
                                     gap=gap,
                                     taper_length=taper_length,
                                     a=a, b=b)

    names_1 = ['launcher_0-', 'launcher_-0', 'launcher_0+', 'launcher_+0']
    position_1 = [chip_size[0] / 2 + 1j * gnd_slot,
                  gnd_slot + 1j * chip_size[1] / 2,
                  chip_size[0] / 2 + 1j * (chip_size[1] - gnd_slot),
                  (chip_size[0] - gnd_slot) + 1j * chip_size[1] / 2]
    degree_1 = list(90 - 90 * np.arange(4))

    names_1 += ['launcher_--', 'launcher_-+', 'launcher_++', 'launcher_+-']
    position_1 += list(
        np.array(position_2) + (1 + 1 / np.sqrt(2)) * gnd_slot * np.array([1 + 1j, 1 - 1j, -1 - 1j, -1 + 1j]))
    degree_1 += list(45 - 90 * np.arange(4))

    for launcher_name in launchers:
        idx_1 = names_1.index(launcher_name)
        xx = chip_1.combine_device(launcher_1, ref=position_1[idx_1], degree=degree_1[idx_1], axis='none',
                                   port='1')

    return chip_1

#%% example
x = new_device(time=time_stamp)
x.gen_gds(marker=True, flux_trap=True, set_zero=True)
