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

def new_device(
        # pad
        pad_length = [50, 60],
        pad_width = [[10, 70],[10, 70]],
        pad_gap = [[6, 42],[6, 42]],
        spacer = 21,
        c_g = [300, 300],
        c_p = [20, 30],
        # sns
        sns_zone = (22, 10.4),
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
    sns_x_shift = pad_width[0][0]/2 - (sns_nanowire_width/2 + sns_nanowire_extension + sns_ghost[1] + sns_protection_gap + w_electrode)

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

    # pad 1
    sns_taper_1 = taper.new_device(length=pad_length[1],
                                   a=pad_width[0][0],
                                   b=pad_gap[0][0],
                                   a2=pad_width[0][1],
                                   b2=pad_gap[0][1],
                                   layer='Nb_inv')

    path = [0]
    path.append(path[-1] + pad_length[0])
    cpw_1 = cpw.new_device(
        path,
        a=pad_width[0][1],
        b=pad_gap[0][1],
        r=r,
        d_rad=d_rad,
        layer='Nb_inv'
    )

    poly_1 = [0]
    poly_1.append(poly_1[-1] + pad_gap[0][1])
    poly_1.append(poly_1[-1] + 1j * (pad_width[0][1] + 2*pad_gap[0][1]))
    poly_1.append(poly_1[-1] - pad_gap[0][1])
    cpw_1.add_geometry('Nb_inv', [poly_1], ref=cpw_1.ports['2'] - 1j*(pad_width[0][1] + 2*pad_gap[0][1])/2)

    cpw_taper_1_ports = sns_taper_1.combine_device(cpw_1, ref=sns_taper_1.ports['2'], degree=0, axis='none', port='1')
    sns_taper_1.ports['2'] = cpw_taper_1_ports['2']
    sns_taper_1_ports = sns_1.combine_device(sns_taper_1, ref=sns_1.ports['270'], degree=-90, axis='none', port='1')

    # pad 2
    sns_taper_2 = taper.new_device(length=pad_length[1],
                                   a=pad_width[1][0],
                                   b=pad_gap[1][0],
                                   a2=pad_width[1][1],
                                   b2=pad_gap[1][1],
                                   layer='Nb_inv')

    path = [0]
    path.append(path[-1] + pad_length[0])
    cpw_2 = cpw.new_device(
        path,
        a=pad_width[1][1],
        b=pad_gap[1][1],
        r=r,
        d_rad=d_rad,
        layer='Nb_inv'
    )

    poly_1 = [0]
    poly_1.append(poly_1[-1] + pad_gap[1][1])
    poly_1.append(poly_1[-1] + 1j * (pad_width[1][1] + 2 * pad_gap[1][1]))
    poly_1.append(poly_1[-1] - pad_gap[1][1])
    cpw_2.add_geometry('Nb_inv', [poly_1], ref=cpw_2.ports['2'] - 1j * (pad_width[1][1] + 2 * pad_gap[1][1]) / 2)

    cpw_taper_2_ports = sns_taper_2.combine_device(cpw_2, ref=sns_taper_2.ports['2'], degree=0, axis='none', port='1')
    sns_taper_2.ports['2'] = cpw_taper_2_ports['2']
    sns_taper_2_ports = sns_1.combine_device(sns_taper_2, ref=sns_taper_1_ports['2'] - 1j*(c_g[1] + pad_gap[0][1] + pad_gap[1][1]), degree=90, axis='none', port='2')

    sns_1.add_port('2', sns_taper_2_ports['1'])

    #%% capacitor 2 ground
    poly_1 = [-(c_g[0] + 2*spacer)/2]
    poly_1.append(poly_1[-1] - 1j * (c_g[1] + spacer + spacer + pad_length[0]))
    poly_1.append(poly_1[-1] + (c_g[0] + 2*spacer))
    poly_1.append(poly_1[-1] + 1j * (c_g[1] + spacer + spacer + pad_length[0]))
    sns_1.add_geometry('SiO2', [poly_1], ref=sns_taper_1_ports['2'])

    poly_2 = [-c_g[0]/ 2]
    poly_2.append(poly_2[-1] - 1j * c_g[1])
    poly_2.append(poly_2[-1] + c_g[0])
    poly_2.append(poly_2[-1] + 1j * c_g[1])

    poly_3 = [-c_p[0] / 2 - 1j * c_g[1]]
    poly_3.append(poly_3[-1] - 1j * (pad_gap[0][1] + c_p[1]))
    poly_3.append(poly_3[-1] + c_p[0])
    poly_3.append(poly_3[-1] + 1j * (pad_gap[0][1] + c_p[1]))

    poly_4 = [-c_p[0] / 2]
    poly_4.append(poly_4[-1] + 1j * (pad_gap[1][1] + c_p[1]))
    poly_4.append(poly_4[-1] + c_p[0])
    poly_4.append(poly_4[-1] - 1j * (pad_gap[1][1] + c_p[1]))

    sns_1.add_geometry('Patch', [poly_2, poly_3, poly_4], ref=sns_taper_1_ports['2'] - 1j*pad_gap[1][1])

    # cpw_taper_1_ports = sns_taper_1.combine_device(cpw_1, ref=sns_taper_1.ports['2'], degree=0, axis='none', port='1')

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
