import numpy as np
import scipy as sci

import datetime
import sys
import os

today = str(datetime.date.today()).split('-')
time_stamp = today[0][-2:] + today[1] + today[2]
device_name = os.path.basename(__file__)[:-3]

sys.path.append('../../repertoire/')
sys.path.append('../../repertoire/device')
from class_device import device
from class_chip import chip
import aux_poly


#%%
import template_1 as chip_template
import cpw_1 as cpw
import cpw_inline_1 as cpw_inline
import cross_1 as cross
import cap_1 as cap
import cap_2 as cap_v2
import taper_1 as taper

#%%
chip_1 = chip_template.new_device(name='FSG',
               time=time_stamp,
               logo='QCD',
               die_size=(15e3, 15e3),
               chip_size=(10e3, 10e3),
               trap_size=(20, 100),
               # launcher
               launchers=['launcher_--', 'launcher_0-', 'launcher_-+', 'launcher_-0', 'launcher_++', 'launcher_0+',
                          'launcher_+-', 'launcher_+0'],
               pad=250,
               taper_length=250,
               gnd_slot=250,
               # general
               a=10, b=6)

#%%
path = [chip_1.ports['launcher_-+'].x]
path.append(path[-1] + (1-1j)*250)
path.append(path[-1].real + 1j*7e3)
path.append(1.5e3 + 1j * 7e3)
dr_cavity_1 = cpw.new_device(path=path)
dr_cavity_1.terminate_port('2', width=22, gap=6, degree=0, layer='Nb_inv')

chip_1.combine_device(dr_cavity_1, degree=0, axis='none', port='1')


cavity_1 = cpw_inline.new_device(pt_start=0,
                        pt_stop=3000,
                        length=14755,
                        N=12,
                        flip=False,
                        zero_pre=False,
                        a=10,
                        b=6,
                        r=50,
                        d_rad=np.pi / 36,
                        layer='Nb_inv'
                )

ports_cavity_1 = chip_1.combine_device(cavity_1, ref= 2e3 + 1j * 7e3, degree=0, axis='none', port='1')

cap_1 = cap.new_device(
        width=(60, 30),
        gap=(6, 6),
        length=(30, 30),
        a=10,
        b=6,
        layer='Nb_inv')

ports_cap_1 = chip_1.combine_device(cap_1, ref=ports_cavity_1['2'].x, degree=90, axis='none', port='outside')

cross_1 = cross.new_device(angle=(0, 90, 180, 270),
                   length=(130, 130, 130, 130),
                   a_list=(24, 24, 24, 24),
                   b_list=(12, 12, 12, 12),
                   c_list=(12, 12, 12, 12),
                   layer='Nb_inv')

ports_cross_1 = chip_1.combine_device(cross_1, ref=ports_cap_1['inside'].x + 6, degree=0, axis='none', port='180')

cap_2 = cap.new_device(
        width=(60, 30),
        gap=(6, 6),
        length=(30, 30),
        a=10,
        b=6,
        layer='Nb_inv')

ports_cap_2 = chip_1.combine_device(cap_2, ref=ports_cross_1['0'].x + 6, degree=270, axis='none', port='inside')

cavity_2 = cpw_inline.new_device(pt_start=0,
                        pt_stop=1500,
                        length=7001,
                        N=12,
                        flip=False,
                        zero_pre=False,
                        a=10,
                        b=6,
                        r=50,
                        d_rad=np.pi / 36,
                        layer='Nb_inv'
                )

ports_cavity_2 = chip_1.combine_device(cavity_2, ref= ports_cap_2['outside'].x, degree=0, axis='none', port='1')

cap_3 = cap_v2.new_device(
        width=(30, 30, 6),
        gap=(6, 6),
        length=(30, 30),
        a=10,
        b=6,
        layer='Nb_inv')

ports_cap_3 = chip_1.combine_device(cap_3, ref=ports_cavity_2['2'].x, degree=90, axis='none', port='outside')

taper_1 = taper.new_device(length=10,
               a=30, b=6,
               a2=10, b2=6,
               form='normal',
               layer='Nb_inv')

ports_taper_1 = chip_1.combine_device(taper_1, ports_cap_3['inside'].x+6, degree=0, axis='none', port='1')

path = [chip_1.ports['launcher_++'].x]
path.append(path[-1] + (-1-1j)*250)
path.append(path[-1].real + 1j*7e3)
path.append(ports_taper_1['2'].x)
dr_cavity_2 = cpw.new_device(path=path)
# dr_cavity_2.terminate_port('2', width=22, gap=6, degree=0, layer='Nb_inv')

chip_1.combine_device(dr_cavity_2, degree=0, axis='none', port='2')


#%%
chip_1.gen_gds(marker=False, flux_trap=False, set_zero=False)