import datetime
import os
import sys

import numpy as np

today = str(datetime.date.today()).split('-')
time_stamp = today[0][-2:] + today[1] + today[2]
device_name = os.path.basename(__file__)[:-3]

sys.path.append('../../repertoire/')
sys.path.append('../../repertoire/device')
from class_device import handshake

# %% dependence
import template_1 as chip_template
import cpw_1 as cpw
import fsg_1 as fsg

# %%
a = 10
b = 6
r = 50
flag_FEM = False

chip_1 = chip_template.new_device(name='FSGx4',
               time=time_stamp,
               logo='QCD',
               die_size=(15e3, 15e3),
               chip_size=(10e3, 10e3),
               trap_size=(5, 20),
               # launcher
               launchers=['launcher_--', 'launcher_0-', 'launcher_-+', 'launcher_-0', 'launcher_++', 'launcher_0+',
                          'launcher_+-', 'launcher_+0'],
               pad=250,
               taper_length=250,
               gnd_slot=250,
               # general
               a=a,
               b=b,
               flag_FEM=flag_FEM)

chip_size = (10e3, 10e3)
x_0 = chip_size[0]/2 + 1j*chip_size[1]/2

cpw_storage = cpw.route(chip_1.ports['launcher_0+'], chip_1.ports['launcher_0-'])
chip_1.combine_device(cpw_storage)

# %%
fsg_1 = fsg.new_device(length_storage=6000,
                       length_output=6059,
                       cap_width=[48, 48, 48],
                       cap_length=[105, 145, 40],
                       cross_width=[48, 24, 48, 24],
                       a=10,
                       b=6,
                       r=50,
                       d_rad=np.pi / 36,
                       layer='Nb_inv')

ports_fsg_1 = chip_1.combine_device(fsg_1, ref=x_0.real + 30 + (a+2*b) + 1j*6e3, axis='none', port='storage')

cpw_output = cpw.route(chip_1.ports['launcher_+0'], ports_fsg_1['output'], r=100)
chip_1.combine_device(cpw_output)

cpw_qubit = cpw.route(chip_1.ports['launcher_++'],
                      handshake(x=ports_fsg_1['qubit_90'].x + (150 + 30j), angle=90), r=100)
cpw_qubit.terminate_port('2', width=22, gap=6)
chip_1.combine_device(cpw_qubit)

# %% source 2
fsg_2 = fsg.new_device(length_storage=6300,
                       length_output=6121,
                       cap_width=[98, 48, 48],
                       cap_length=[125, 125, 40],
                       cross_width=[48, 24, 48, 24],
                       a=10,
                       b=6,
                       r=50,
                       d_rad=np.pi / 36,
                       layer='Nb_inv')

ports_fsg_2 = chip_1.combine_device(fsg_2, ref=x_0.real - 30 - (a+2*b) + 1j*4e3, axis='y', port='storage')

cpw_output_2 = cpw.route(chip_1.ports['launcher_-0'], ports_fsg_2['output'], r=100)
chip_1.combine_device(cpw_output_2)

cpw_qubit_2 = cpw.route(chip_1.ports['launcher_--'],
                        handshake(x=ports_fsg_2['qubit_270'].x + (-150 - 30j), angle=270), r=100)
cpw_qubit_2.terminate_port('2', width=22, gap=6)
chip_1.combine_device(cpw_qubit_2)

# %% source 3
fsg_3 = fsg.new_device(length_storage=6620,
                       length_output=6124,
                       cap_width=[148, 48, 48],
                       cap_length=[145, 125, 40],
                       cross_width=[48, 24, 48, 24],
                       a=10,
                       b=6,
                       r=50,
                       d_rad=np.pi / 36,
                       layer='Nb_inv')

ports_fsg_3 = chip_1.combine_device(fsg_3, ref=x_0.real + 30 + (a+2*b) + 1j*2e3, axis='none', port='storage')

cpw_output_3 = cpw.route(chip_1.ports['launcher_+-'], ports_fsg_3['output'], r=100)
chip_1.combine_device(cpw_output_3)

# %% source 4
fsg_4 = fsg.new_device(length_storage=7350,
                       length_output=6117,
                       cap_width=[148, 48, 48],
                       cap_length=[165, 125, 40],
                       cross_width=[48, 24, 48, 24],
                       a=10,
                       b=6,
                       r=50,
                       d_rad=np.pi / 36,
                       layer='Nb_inv')

ports_fsg_4 = chip_1.combine_device(fsg_4, ref=x_0.real - 30 - (a+2*b) + 1j*8e3, axis='y', port='storage')

cpw_output_4 = cpw.route(chip_1.ports['launcher_-+'], ports_fsg_4['output'], r=100)
chip_1.combine_device(cpw_output_4)

# %%
chip_1.gen_gds(marker=not(flag_FEM), flux_trap=True, set_zero=True)