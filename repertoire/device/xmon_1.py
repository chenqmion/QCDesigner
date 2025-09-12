import sys

import numpy as np

sys.path.append('../')
from class_device import device
from class_chip import chip

import aux_poly
import cross_1 as cross
import cap_1 as cap
import squid_1 as squid
import flux_1 as flux
import drive_1 as drive
import lambda4_1 as lambda4

def new_device(# cross
                cross_angle=[0, 90, 180, 270],
                cross_length=[130, 130, 130, 130],
                cross_a_list=[8, 8, 8, 8],
                cross_b_list=[8, 8, 8, 8],
                cross_c_list=[8, 8, 8, 8],

                # squid
                squid_port = '270',
                squid_width = 10, squid_height = 4, nanowire_width = 0.2,
                nanowire_extension = 1, contact_gap = 0.5, protection_gap = 1.5, w_electrode = 3,

                # z line
                z_port = '270',
                z_gap = 3, z_length=[10, 50], z_tip=[2, 20],

                # xy line
                xy_port = '180',
                xy_gap = 30, xy_length=[10, 50],

                # ro
                ro_port = '90',
                ro_gap = 5, cap_width = [50, 30], cap_gap=[5, 10], cap_length = [65,10],
                ro_length = 2500, ro_height = [1000, 200], ro_width = [500, 300], ro_mode = 'incompact',

                # general
                a=10, b=6, a2=3, b2=3, r=50, d_rad=np.pi / 36, layer='Nb_inv'
                ):

    xmon_1 = device()

    #%% cross
    if squid_port != None:
        idx_port_squid = list(cross_angle).index(int(squid_port))
        cross_c_list2 = cross_c_list.copy()
        cross_c_list2[idx_port_squid] = 0
    else:
        cross_c_list2 = cross_c_list

    cross_1 = cross.new_device(angle=cross_angle,
                  length=cross_length,
                  a_list=cross_a_list,
                  b_list=cross_b_list,
                  c_list=cross_c_list2,
                  layer=layer)

    ports_cross_1 = xmon_1.combine_device(cross_1, ref=None, degree=0, axis='none', port='0')
    xmon_1.ports = ports_cross_1

    #%% squid
    if squid_port != None:
        squid_zone = [cross_a_list[idx_port_squid] + 2*cross_b_list[idx_port_squid], cross_c_list[idx_port_squid]]
        squid_1 = squid.new_device(zone=squid_zone, squid_width=squid_width, squid_height=squid_height, nanowire_width=nanowire_width,
                         nanowire_extension=nanowire_extension, contact_gap=contact_gap, protection_gap=protection_gap,
                         w_electrode=w_electrode)

        ports_squid_1 = xmon_1.combine_device(squid_1, ref=xmon_1.ports[squid_port],
                                              degree=int(squid_port) + 90, axis='none', port='90')
        xmon_1.ports[squid_port] = ports_squid_1['270']

    #%% z line
    if z_port != None:
        z_1 = flux.new_device(length=z_length, tip=z_tip, a=a, b=b, a2=a2, b2=b2, layer=layer)
        ports_z_1 = xmon_1.combine_device(z_1, ref=xmon_1.ports[z_port] + z_gap*np.exp(1j*int(z_port)*np.pi/180),
                                              degree=int(z_port) + 180, axis='none', port='output')
        xmon_1.ports[z_port] = ports_z_1['input']

    #%% xy line
    if xy_port != None:
        xy_1 = drive.new_device(length=xy_length, a=a, b=b, a2=a2, b2=b2, layer=layer)
        ports_xy_1 = xmon_1.combine_device(xy_1, ref=xmon_1.ports[xy_port] + xy_gap*np.exp(1j*int(xy_port)*np.pi/180),
                                              degree=int(xy_port) + 180, axis='none', port='output')
        xmon_1.ports[xy_port] = ports_xy_1['input']


    #%% ro
    if ro_port != None:
        cap_1 = cap.new_device(width=cap_width, gap=cap_gap, length=cap_length, a=a, b=b, layer=layer)
        ports_cap_1 = xmon_1.combine_device(cap_1, ref=xmon_1.ports[ro_port] + ro_gap*np.exp(1j*int(ro_port)*np.pi/180),
                                              degree=int(ro_port) - 90, axis='none', port='inside')

        lambda4_1 = lambda4.new_device(length=ro_length, height=ro_height, width=ro_width, mode=ro_mode,
                   a=a, b=b, r=r, d_rad=d_rad, layer=layer)

        ports_lambda4_1 = xmon_1.combine_device(lambda4_1, ref=ports_cap_1['outside'], degree=int(ro_port) - 90, axis='none', port='1')

        ref_port = ports_cap_1['outside'] - ro_width[0]/2 + 1j*(ro_height[0] + a/2 + b)
        xmon_1.ports[ro_port] = ref_port

    return xmon_1


# x = new_device()
#
# chip_1 = design(name='xmon',
#               time='250611',
#               logo='QCD',
#               die_size=(15e3, 15e3),
#               chip_size=(10e3, 10e3),
#               trap_size=(20, 100))
# chip_1.add_device('xmon', x, ref=5e3 * (1 + 1j), degree=0, axis='none', port='0')
# chip_1.gen_gds(marker=True, flux_trap=True, set_zero=True)
