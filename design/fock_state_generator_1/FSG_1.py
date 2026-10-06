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
               pad=400,
               gap=240,
               taper_length=400,
               gnd_slot=350,
               # general
               a=10, b=6)

#%%


#%%
chip_1.gen_gds(marker=True, flux_trap=True, set_zero=True)