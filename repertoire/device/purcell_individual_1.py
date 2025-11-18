import datetime
import sys

import numpy as np

today = str(datetime.date.today()).split('-')
time_stamp = today[0][-2:] + today[1] + today[2]

sys.path.append('../')
from class_chip import chip

import cpw_1 as cpw
import lambda4_1 as lambda4
import cross_1 as cross
import finger_1 as finger

import bolometer_1 as bolometer


def new_device(
        ro_length=[4250, 1400],
        ro_width=[250, 250, 100],
        purcell_length=[4250, 1400, 100],
        purcell_width=[650, 250, 100],
        meander_height=[300, 500],
        meander_gap=150,
        # finger
        finger_gap=5,
        finger_length=[[40, 15], [110, 50]],
        finger_number=[2, 5],
        # sns
        sns_zone=(22, 12.85),
        sns_island_width=[0.5, 0.5, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.5],
        sns_island_gap=[1, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25],
        sns_contact_gap=0.5,
        sns_protection_gap=1.5,
        sns_nanowire_width=0.15,
        sns_nanowire_extension=1,
        sns_ghost=[0.1, 0.8],
        # parallel plate
        pad_spacer=20,
        pad_c_g=[240, 240],
        pad_c_p=[20, 36],
        # common
        a=10, b=6, r=50, d_rad=np.pi / 36, w_electrode=3, layer='Nb_inv'
):
    # %%
    ro_width_1 = ro_width[0] - ro_width[1]
    ro_width_2 = ro_width[1]

    purcell_width_1 = purcell_width[0] - purcell_width[1]
    purcell_width_2 = purcell_width[1]

    if ro_width_1 != 0:
        ro_height_1a = ro_length[1] - (a + 2 * b) - (
                    meander_height[1] + meander_gap + r + ro_width_1 - 2 * r + np.pi * r)
    else:
        ro_height_1a = ro_length[1] - (a + 2 * b) - (meander_height[1] + meander_gap + r)

    if purcell_width_1 != 0:
        purcell_height_1a = purcell_length[1] - (a + 2 * b) - (
                    meander_height[0] + meander_gap + r + purcell_width_1 - 2 * r + np.pi * r)
    else:
        purcell_height_1a = purcell_length[1] - (a + 2 * b) - (meander_height[0] + meander_gap + r)

    # %% readout resonator
    path = [0]
    path.append(path[-1] + 1j * ro_height_1a)
    path.append(path[-1] - ro_width_1)
    path.append(path[-1] + 1j * (meander_height[1] + meander_gap + r))
    cpw_1 = cpw.new_device(path, a=a, b=b, r=r, d_rad=d_rad, layer=layer)

    finger_1_length = finger_length[0][0] + 2 * finger_length[0][1]
    cross_1 = cross.new_device(angle=(0, 90, 270),
                               length=(meander_gap / 2 - finger_1_length / 2, (a + 2 * b) / 2, (a + 2 * b) / 2),
                               a_list=(finger_gap, a, a),
                               b_list=(finger_gap * b / a, b, b),
                               c_list=(0, 0, 0),
                               layer=layer)

    cross_1_ports = cpw_1.combine_device(cross_1, ref=cpw_1.ports['2'], degree=0, axis='none', port='270')

    cpw_2 = lambda4.new_device(length=ro_length[0] - ro_length[1],
                               height=[(meander_height[0] + meander_gap + r) - meander_gap, r],
                               width=(ro_width_2, ro_width[2]), mode='incompact', a=a, b=b, r=r, d_rad=d_rad,
                               layer=layer)
    cpw_2_ports = cpw_1.combine_device(cpw_2, ref=cross_1_ports['90'], degree=0, axis='none', port='1')

    # %% finger 1
    finger_1 = finger.new_device(width=5 * (3 * finger_number[0] - 1),
                                 gap=[finger_gap, 5 * (3 * finger_number[0] - 1) * b / a],
                                 length=finger_length[0],
                                 N=finger_number[0],
                                 a=[finger_gap, finger_gap],
                                 b=[finger_gap * b / a, finger_gap * b / a],
                                 layer=layer)
    finger_1_ports = cpw_1.combine_device(finger_1, ref=cross_1_ports['0'], degree=0, axis='none', port='1')

    # %% purcell filter
    path = [0]
    path.append(path[-1] + 1j * purcell_height_1a)
    path.append(path[-1] - purcell_width_1)
    path.append(path[-1] + 1j * (meander_height[0] + meander_gap + r))
    cpw_1b = cpw.new_device(path, a=a, b=b, r=r, d_rad=d_rad, layer=layer)
    cpw_1b_ports = cpw_1.combine_device(cpw_1b, ref=cpw_2_ports['1'] + meander_gap, degree=180, axis='none', port='2')
    cross_1b_ports = cpw_1.combine_device(cross_1, ref=cpw_1b_ports['2'], degree=0, axis='y', port='90')

    cpw_2b = lambda4.new_device(length=purcell_length[0] - purcell_length[1] - purcell_length[2],
                                height=[((meander_height[1] + meander_gap + r) - meander_gap) - (a + 2 * b), r],
                                width=(purcell_width_2, purcell_width[2]),
                                mode='incompact', a=a, b=b, r=r, d_rad=d_rad, layer=layer)
    cpw_2b_ports = cpw_1.combine_device(cpw_2b, ref=cross_1b_ports['270'], degree=180, axis='none', port='1')

    cross_2b = cross.new_device(angle=(0, 90, 270),
                                length=(purcell_length[2], purcell_length[2], 11),
                                a_list=(a, a, a),
                                b_list=(b, b, b),
                                c_list=(0, 0, 0),
                                layer=layer)

    cross_2b_ports = cpw_1.combine_device(cross_2b, ref=cpw_2b_ports['2'], degree=0, axis='none', port='270')

    # path = [0]
    # path.append(path[-1] + (purcell_width[1]-purcell_width[2] - (a/2 + b)))
    # path.append(path[-1] + 1j*(purcell_width[1]-purcell_width[2] - (a/2 + b)))
    # path.append(path[-1] + 1j*(purcell_length[2] - np.pi*r/2 - 2*(purcell_width[1]-purcell_width[2]-(a/2 + b)-r)))
    #
    # cpw_3b = cpw.new_device(path, a=a, b=b, r=r, d_rad=d_rad, layer=layer)
    # cpw_3b_ports = cpw_1.combine_device(cpw_3b, ref=cross_2b_ports['0'], degree=0, axis='none', port='1')

    # %% finger 2
    finger_2 = finger.new_device(width=5 * (3 * finger_number[1] - 1),
                                 gap=[finger_gap, 5 * (3 * finger_number[1] - 1) * b / a],
                                 length=finger_length[1], N=finger_number[1],
                                 a=[a, finger_gap],
                                 b=[b, finger_gap * b / a],
                                 layer=layer)
    finger_2_ports = cpw_1.combine_device(finger_2, ref=cpw_1b_ports['1'], degree=90, axis='none', port='1')

    finger_3 = finger.new_device(width=5 * (3 * finger_number[1] - 1),
                                 gap=[finger_gap, 5 * (3 * finger_number[1] - 1) * b / a],
                                 length=finger_length[1], N=finger_number[1],
                                 a=[5 * (3 * finger_number[1] - 1), a],
                                 b=[5 * (3 * finger_number[1] - 1) * b / a, b],
                                 layer=layer)

    finger_3_ports = cpw_1.combine_device(finger_3,
                                          ref=cpw_1.ports['1'],
                                          degree=90,
                                          axis='none',
                                          port='2')

    # %% bolometer
    bolometer_1 = bolometer.new_device(
        pad_length=[finger_length[1][0] / 2, finger_length[1][1]],
        pad_width=[[a, finger_gap * (3 * finger_number[1] - 1)], [finger_gap, finger_gap * (3 * finger_number[1] - 1)]],
        pad_gap=[[b, finger_gap * (3 * finger_number[1] - 1) * b / a],
                 [finger_gap * b / a, finger_gap * (3 * finger_number[1] - 1) * b / a]],
        spacer=pad_spacer,
        c_g=pad_c_g,
        c_p=pad_c_p,
        sns_zone=sns_zone,
        sns_island_width=sns_island_width,
        sns_island_gap=sns_island_gap,
        sns_contact_gap=sns_contact_gap,
        sns_protection_gap=sns_protection_gap,
        sns_nanowire_width=sns_nanowire_width,
        sns_nanowire_extension=sns_nanowire_extension,
        sns_ghost=sns_ghost,
        w_electrode=w_electrode
    )

    # bolometer_1_ports = cpw_1.combine_device(bolometer_1, ref=cross_2b_ports['90'], degree=0, axis='x', port='1')
    bolometer_1_ports = cpw_1.combine_device(bolometer_1, ref=cross_2b_ports['90'].real + 1j * finger_2_ports['2'].imag,
                                             degree=0, axis='x', port='2')

    return cpw_1


x = new_device()

chip_1 = chip(name='purcell',
              time='250819',
              logo='QCD',
              die_size=(15e3, 15e3),
              chip_size=(10e3, 10e3),
              trap_size=(20, 100))

chip_1.add_device('purcell', x, ref=5e3 * (1 + 1j), degree=0, axis='none', port='1')
chip_1.gen_gds(marker=True, flux_trap=False, set_zero=False)
