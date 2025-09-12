import sys

import numpy as np
import datetime

today = str(datetime.date.today()).split('-')
time_stamp = today[0][-2:] + today[1] + today[2]

sys.path.append('../')
from class_chip import chip

import cpw_1 as cpw
import cpw_offline_1 as cpw_offline
import lambda4_1 as lambda4
import cross_1 as cross
import finger_1 as finger
import sns_1 as sns
import taper_1 as taper

import capacitor_cross_1 as capacitor_cross

def new_device(
        # pad
        c_g = [300, 300],
        c_p = [20, 30],
        ald_protection = 10,
        a2 = 10,
        b2 = 10,
        # sns
        sns_zone = (22, 12.85),
        sns_island_width=[0.5, 0.5, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.5],
        sns_island_gap=[1, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25],
        sns_contact_gap=0.5,
        sns_protection_gap=1.5,
        sns_nanowire_width=0.15,
        sns_nanowire_extension=1,
        sns_ghost=[0.1, 0.8],
        # common
        a=10, b=6, r=50, d_rad=np.pi / 36, w_electrode=3
        ):

    #%% bolometer
    sns_x_shift = a/2 - (sns_nanowire_width/2 + sns_nanowire_extension + sns_ghost[1] + sns_protection_gap + w_electrode)

    sns_1 = sns.new_device(
        zone=sns_zone,
        island_width=sns_island_width,
        island_gap=sns_island_gap,
        with_absorber=True,
        contact_gap=sns_contact_gap,
        protection_gap=sns_protection_gap,
        nanowire_width=sns_nanowire_width,
        nanowire_extension=sns_nanowire_extension,
        x_shift = sns_x_shift,
        ghost=sns_ghost,
        w_electrode=w_electrode
    )

    sns_1.add_port('1', sns_1.ports['90'])

    # capacitor
    cap_1 = capacitor_cross.new_device(
        gnd_size = c_g,
        cap_size = c_p,
        protection_gap = ald_protection,
        a=[a2, a],
        b=[b2, b],
        layer='Nb_inv'
    )

    cap_ports = sns_1.combine_device(cap_1, ref=sns_1.ports['270'], degree=0, axis='x', port='bottom')
    sns_1.ports['2'] = cap_ports['top']

    return sns_1

x = new_device()

chip_1 = chip(name='bolo',
              time=time_stamp,
              logo='QCD',
              die_size=(15e3, 15e3),
              chip_size=(10e3, 10e3),
              trap_size=(20, 100))

chip_1.add_device('bolo', x, ref=5e3 * (1 + 1j), degree=0, axis='none', port='1')
chip_1.gen_gds(marker=True, flux_trap=False, set_zero=True)
