import sys

import numpy as np

sys.path.append('../')
import geometry_class as geo

import launcher_1


def new_chip(name='test',
             time='240727',
             logo='QCD',
             chip_size=(10e3, 10e3),
             gnd_size=(96e2, 96e2),
             layers_ebl=['AuPd', 'Al'],
             launchers=['WS', 'WN', 'NW', 'NE', 'EN', 'ES', 'SE', 'SW'],
             launcher_size=(300, 180, 200),
             launcher_arrange=(2200, 100),
             mode='experiment',
             a=10,
             b=6
             ):
    chp = geo.chip(name=name, time=time, logo=logo)

    if mode == 'experiment':
        # %% gnd
        edge = new_edge(chip_size=chip_size,
                        gnd_size=gnd_size,
                        indicator=True,
                        )
        chp.add_device(edge)

        # %% marker
        marker = marker_1.new_marker(chip_size=chip_size,
                                     gnd_size=gnd_size,
                                     layers_ebl=layers_ebl,
                                     diagonal_launcher=(launcher_arrange[0] == 0)
                                     )
        chp.add_device(marker)

        # %% information
        if launcher_arrange[0] != 0:
            str_name = marker_1.new_text(name,
                                         position=((chip_size[0] - gnd_size[0]) / 2 + 100) +
                                                  1j * ((chip_size[1] + gnd_size[1]) / 2 - 400))
            chp.add_device(str_name)

            str_time = marker_1.new_text(time,
                                         position=((chip_size[0] + gnd_size[0]) / 2 - 1266.667) +
                                                  1j * ((chip_size[1] + gnd_size[1]) / 2 - 400))
            chp.add_device(str_time)

            str_logo = marker_1.new_text(logo,
                                         position=((chip_size[0] - gnd_size[0]) / 2 + 100) +
                                                  1j * ((chip_size[1] - gnd_size[1]) / 2 + 33.333))
            chp.add_device(str_logo)
        else:
            pt_off = ((chip_size[1] - gnd_size[1]) / 2 + 2200) + 1j * ((chip_size[1] - gnd_size[1]) / 2 + 400)

            str_name = marker_1.new_text(name, position=(pt_off.real + 200, chip_size[1] - pt_off.imag))
            chp.add_device(str_name)

            str_time = marker_1.new_text(time, position=(chip_size[0] - pt_off.real - 1640, chip_size[1] - pt_off.imag))
            chp.add_device(str_time)

            str_logo = marker_1.new_text(logo, position=(pt_off.real + 200, pt_off.imag - 300))
            chp.add_device(str_logo)

    # %% launcher
    dic_launcher = {}

    if launcher_arrange[0] != 0:
        dic_launcher['WS'] = [((chip_size[0] - gnd_size[0]) / 2)
                              + 1j * (chip_size[1] / 2 - launcher_arrange[0]),
                              0]
        dic_launcher['WN'] = [((chip_size[0] - gnd_size[0]) / 2)
                              + 1j * (chip_size[1] / 2 + launcher_arrange[0]),
                              0]
        dic_launcher['NW'] = [(chip_size[0] / 2 - launcher_arrange[0])
                              + 1j * ((chip_size[1] + gnd_size[1]) / 2),
                              -90]
        dic_launcher['NE'] = [(chip_size[0] / 2 + launcher_arrange[0])
                              + 1j * ((chip_size[1] + gnd_size[1]) / 2),
                              -90]
        dic_launcher['EN'] = [((chip_size[0] + gnd_size[0]) / 2)
                              + 1j * (chip_size[1] / 2 + launcher_arrange[0]),
                              180]
        dic_launcher['ES'] = [((chip_size[0] + gnd_size[0]) / 2)
                              + 1j * (chip_size[1] / 2 - launcher_arrange[0]),
                              180]
        dic_launcher['SE'] = [(chip_size[0] / 2 + launcher_arrange[0])
                              + 1j * ((chip_size[1] - gnd_size[1]) / 2),
                              90]
        dic_launcher['SW'] = [(chip_size[0] / 2 - launcher_arrange[0])
                              + 1j * ((chip_size[1] - gnd_size[1]) / 2),
                              90]
    else:
        dic_launcher['--'] = [((chip_size[0] - gnd_size[0]) / 2 + launcher_arrange[1]) + 1j * (
                (chip_size[0] - gnd_size[0]) / 2 + launcher_arrange[1]), 45]
        dic_launcher['-0'] = [((chip_size[0] - gnd_size[0]) / 2) + 1j * (chip_size[1] / 2), 0]
        dic_launcher['-+'] = [((chip_size[0] - gnd_size[0]) / 2 + launcher_arrange[1]) + 1j * (
                (chip_size[1] + gnd_size[1]) / 2 - launcher_arrange[1]), -45]
        dic_launcher['0+'] = [(chip_size[0] / 2) + 1j * ((chip_size[0] + gnd_size[0]) / 2), -90]
        dic_launcher['++'] = [((chip_size[0] + gnd_size[0]) / 2 - launcher_arrange[1]) + 1j * (
                (chip_size[0] + gnd_size[0]) / 2 - launcher_arrange[1]), -135]
        dic_launcher['+0'] = [((chip_size[0] + gnd_size[0]) / 2) + 1j * (chip_size[1] / 2), 180]
        dic_launcher['+-'] = [((chip_size[0] + gnd_size[0]) / 2 - launcher_arrange[1]) + 1j * (
                (chip_size[1] - gnd_size[1]) / 2 + launcher_arrange[1]), 135]
        dic_launcher['0-'] = [(chip_size[0] / 2) + 1j * ((chip_size[1] - gnd_size[1]) / 2), 90]

    launcher_ports = {}
    launcher = launcher_1.new_launcher(pad=launcher_size[0], gap=launcher_size[1], taper_length=launcher_size[2],
                                       gnd_slot=launcher_arrange[1], a=a, b=b)

    patch = geo.device()
    poly1 = []
    poly1.append(-launcher_arrange[1] - 1j * launcher_arrange[1])
    poly1.append(-launcher_arrange[1] + 1j * launcher_arrange[1])
    poly1.append(launcher_arrange[1] - 1j * launcher_arrange[1])
    patch.add_geometry('Nb_inv', [poly1])

    for name_launcher in launchers:
        if mode == 'experiment':
            new_ports = chp.add_device(launcher, ref=dic_launcher[name_launcher][0],
                                       degree=dic_launcher[name_launcher][1], port=1)

            if not ('0' in name_launcher):
                chp.add_device(patch, ref=dic_launcher[name_launcher][0],
                               degree=dic_launcher[name_launcher][1] - 45, port=1)

            launcher_ports[name_launcher] = new_ports['2']
        else:
            ref_port = geo.ope_rotate([launcher.ports['2']], origin=0,
                                      degree=dic_launcher[name_launcher][1])
            ref_port2 = np.add(ref_port[0], dic_launcher[name_launcher][0])

            launcher_ports[name_launcher] = ref_port2

    return [chp, launcher_ports]


def new_edge(chip_size=(10e3, 10e3),
             gnd_size=(96e2, 96e2),
             indicator=True,
             ):
    # %% edge
    edge = geo.device()

    poly_1 = []
    poly_1.append(0)
    poly_1.append(1j * chip_size[1])
    poly_1.append(chip_size[0] + 1j * chip_size[1])
    poly_1.append(chip_size[0])
    # poly_1.append((0, 0))

    poly_2 = []
    poly_2.append((chip_size[0] - gnd_size[0]) / 2
                  + 1j * (chip_size[1] - gnd_size[1]) / 2)
    poly_2.append((chip_size[0] - gnd_size[0]) / 2
                  + 1j * (chip_size[1] + gnd_size[1]) / 2)
    poly_2.append((chip_size[0] + gnd_size[0]) / 2
                  + 1j * (chip_size[1] + gnd_size[1]) / 2)
    poly_2.append((chip_size[0] + gnd_size[0]) / 2
                  + 1j * (chip_size[1] - gnd_size[1]) / 2)

    poly_1 = geo.poly_hole(poly_1, poly_2)
    if indicator == True:
        poly_3 = []
        poly_3.append(-100 - 100j)
        poly_3.append(-100 + 1000j)
        poly_3.append(100 + 1000j)
        poly_3.append(100 + 100j)
        poly_3.append(1000 + 100j)
        poly_3.append(1000 - 100j)

        poly_3 = np.array(poly_3) + ((chip_size[0] - gnd_size[0]) / 2 - 500) + 1j * (
                (chip_size[0] - gnd_size[0]) / 2 - 500)
        poly_1 = geo.poly_hole(poly_1, poly_3)

    edge.add_geometry('Nb_inv', [poly_1])

    return edge
