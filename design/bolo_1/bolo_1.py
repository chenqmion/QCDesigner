import datetime
import os
import sys

import numpy as np

today = str(datetime.date.today()).split('-')
time_stamp = today[0][-2:] + today[1] + today[2]
device_name = os.path.basename(__file__)[:-3]

sys.path.append('../../repertoire/')
sys.path.append('../../repertoire/device')
from class_device import device, handshake

# %% dependence
import cpw_inline_1 as cpw_inline
import cross_1 as cross
import cap_1 as cap
import finger_1 as finger
import lambda4_inline as lambda4


# %% design
def new_device(
        length_storage=6000,
        length_output=6060,
        cap_width=[48, 48, 48],
        cap_length=[105, 145, 40],
        cross_width=[48, 24, 48, 24],
        a=10,
        b=6,
        r=50,
        d_rad=np.pi / 36,
        layer='Nb_inv'):

    chip_1 = device()

    # %% storage cavity
    cavity_1 = lambda4.new_device(length=length_storage, height=1500, width=50, N=10,
                   a=a, b=b, r=r, d_rad=d_rad, layer=layer)

    ports_cavity_1 = chip_1.combine_device(cavity_1, ref=0, degree=90, axis='none', port='couple')
    chip_1.add_port('storage', 0, 180)

    cap_1 = cap.new_device(
            width=(cross_width[2] + 4*3, cap_width[0]),
            gap=(3, b),
            length=(cap_length[0], a),
            a=a,
            b=b,
            layer=layer)

    ports_cap_1 = chip_1.combine_device(cap_1, port='outside', target=ports_cavity_1['open'])

    cross_1 = cross.new_device(angle=(0, 90, 180, 270),
                       length=(cap_length[1]-3 + 3*cross_width[1]/2, 150, cap_length[0]-3 + 3*cross_width[1]/2, 150),
                       a_list=cross_width,
                       b_list=(3, cross_width[1], 3, cross_width[3]),
                       c_list=(3, 20, 3, 20),
                       layer=layer)

    ports_cross_1 = chip_1.combine_device(cross_1, port='180',
        target=handshake(x=ports_cap_1['inside'].x + 3 * np.exp(1j * ports_cap_1['inside'].angle * np.pi / 180),
                         angle=ports_cap_1['inside'].angle))

    chip_1.add_port('qubit_90', ports_cross_1['90'].x, 90)
    chip_1.add_port('qubit_270', ports_cross_1['270'].x, 270)

    cap_2 = cap.new_device(
            width=(cross_width[0] + 4*3, cap_width[1]),
            gap=(3, b),
            length=(cap_length[1], a),
            a=a,
            b=b,
            layer=layer)

    ports_cap_2 = chip_1.combine_device(cap_2, port='inside',
        target=handshake(x=ports_cross_1['0'].x + 3 * np.exp(1j * ports_cross_1['0'].angle * np.pi / 180),
                         angle=ports_cross_1['0'].angle))

    cavity_2 = cpw_inline.new_device(pt_start=0,
                            pt_stop=1500,
                            length=length_output,
                            N=10,
                            flip=False,
                            zero_pre=False,
                            a=a,
                            b=b,
                            r=r,
                            d_rad=d_rad,
                            layer=layer
                    )

    ports_cavity_2 = chip_1.combine_device(cavity_2, port='1', target=ports_cap_2['outside'])

    cap_3 = finger.new_device(
        finger_width=5,
        finger_gap=[5, 12],
        length=[100, 50],
        N=3,
        a=[10, 10],
        b=[6, 6]
    )

    # cap_3 = cap_v2.new_device(
    #         width=(cross_width[0], cap_width[2], 3),
    #         gap=(3, b),
    #         length=(cap_length[2], a),
    #         a=a,
    #         b=b,
    #         layer=layer)

    ports_cap_3 = chip_1.combine_device(cap_3, port='1', target=ports_cavity_2['2'])

    # taper_1 = taper.new_device(length=20,
    #                a=cross_width[0], b=3,
    #                a2=a, b2=b,
    #                form='normal',
    #                layer=layer)
    #
    # ports_taper_1 = chip_1.combine_device(taper_1, ports_cap_3['inside'].x, degree=0, axis='none', port='1')

    chip_1.add_port('output', ports_cap_3['2'].x, ports_cap_3['2'].angle)

    return chip_1
