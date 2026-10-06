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
                        pt_stop=2000,
                        length=14755,
                        N=16,
                        flip=False,
                        zero_pre=False,
                        a=10,
                        b=6,
                        r=50,
                        d_rad=np.pi / 36,
                        layer='Nb_inv'
                )

chip_1.combine_device(cavity_1, ref= 2e3 + 1j * 7e3, degree=0, axis='none', port='1')

cavity_2 = cpw_inline.new_device(pt_start=0,
                        pt_stop=1000,
                        length=701,
                        N=0,
                        flip=False,
                        zero_pre=False,
                        a=10,
                        b=6,
                        r=50,
                        d_rad=np.pi / 36,
                        layer='Nb_inv'
                )

chip_1.combine_device(cavity_2, ref= 7e3 + 1j * 7e3, degree=0, axis='none', port='1')


#%%
chip_1.gen_gds(marker=False, flux_trap=False, set_zero=False)