import sys

import numpy as np

sys.path.append('../')
import geometry_class as geo

import xmon_1


def new_resonator(res_length=5000, res_width=500, res_N=8,
                  cap_width=[50, 100], cap_gap=[6, 12], cap_length=[100, 50],
                  # xy
                  xy_length=(10, 10, 50), xy_cap=3, xy_gap=10, xy_distance=500,
                  # g
                  g_length=[50, 50], g_a=[3, 3], g_b=[3, 3], curl=True,
                  JJ_span=(24, 8), nanowire_height=4, nanowire_gap=0.5, nanowire_width=0.2,
                  nanowire_extension=1, w_electrode=3, protection_gap=1.5,
                  z_length=(10, 10, 50), z_width=(5, 20), z_gap=5,
                  # general
                  a=10, b=6, r=50, d_rad=np.pi / 36, a2=5, b2=3):
    resonator = geo.device()

    cap = xmon_1.cap_1(width=cap_width, gap=cap_gap, length=cap_length, a=a, b=b)
    cap_ports = resonator.combine_device(cap, ref=0, degree=-90, port=1)

    res_length1 = res_length - xy_distance
    res_N1 = np.round(res_length1 / res_length * res_N, 0).astype(int)
    res_N2 = res_N - res_N1

    if res_length1 > res_N1 * (res_width - 2 * r + np.pi * r):
        cpw = cpw_meander_1.cpw_inline(length=res_length1, width=res_width, N=res_N1)
    else:
        cpw = cpw_1.new_cpw(path=[0, res_length1], a=a, b=b, r=r)
    cpw_ports = resonator.combine_device(cpw, ref=cap_ports['2'], axis='x', port=1)

    if xy_distance > res_N2 * (res_width - 2 * r + np.pi * r):
        cpw2 = cpw_meander_1.cpw_inline(length=xy_distance, width=res_width, N=res_N2)
    else:
        cpw2 = cpw_1.new_cpw(path=[0, xy_distance], a=a, b=b, r=r)
    cpw2_ports = resonator.combine_device(cpw2, ref=cpw_ports['2'], port=1)

    # xy
    ref_xy = cpw_ports['2'] - 1j * (a / 2 + b + xy_cap + xy_gap)
    xy = xmon_1.xy_1(length=xy_length, cap=xy_cap, a=a, b=b, a2=a2, b2=b2)
    xy_ports = resonator.combine_device(xy, ref=ref_xy, degree=90, port=2)

    # g line
    gmon = geo.device()

    len_1 = JJ_span[1] / 2 - nanowire_height - (g_a[0] / 2 + g_b[0])

    cross = xmon_1.cross_1(angle=(0, 90, 180, 270), length=(len_1, g_a[1] / 2, g_a[0] / 2 + g_b[0], a / 2 + b),
                           a_list=(g_a[1], g_a[0], a, g_a[0]), b_list=(g_b[1], g_b[0], b, g_b[0]),
                           cap=(0, g_b[1], 0, 0))
    cross_ports1 = gmon.combine_device(cross, ref=0, port=3)
    cross_ports2 = gmon.combine_device(cross, ref=JJ_span[1], degree=0, axis='y', port=3)

    if curl:
        path = [0]
        path.append(path[-1] - 1j * (2 * r))
        path.append(path[-1] - r)
        cpw = cpw_1.new_cpw(path=np.squeeze(path), a=g_a[0], b=g_b[0], r=r)

        cpw1_1_ports = gmon.combine_device(cpw, ref=cross_ports1['4'], port=1)
        cpw2_1_ports = gmon.combine_device(cpw, ref=cross_ports2['4'], axis='y', port=1)

        cpw1_2 = cpw_meander_1.cpw_offline(pt_start=0,
                                           length=g_length[0] - (r + np.pi * r / 2), width=100, N=4,
                                           a=g_a[0], b=g_b[0], r=r, d_rad=d_rad, mode='compact')
        cpw1_2_ports = gmon.combine_device(cpw1_2, ref=cpw1_1_ports['2'], axis='y', port=1)

        cpw2_2 = cpw_meander_1.cpw_offline(pt_start=0,
                                           length=g_length[1] - (r + np.pi * r / 2), width=100, N=4,
                                           a=g_a[0], b=g_b[0], r=r, d_rad=d_rad, mode='compact')
        cpw2_2_ports = gmon.combine_device(cpw2_2, ref=cpw2_1_ports['2'], port=1)
    else:
        path = [0]
        path.append(path[-1] - 1j * g_length[0])
        cpw1 = cpw_1.new_cpw(path=np.squeeze(path), a=g_a[0], b=g_b[0], r=r)
        cpw1_2_ports = gmon.combine_device(cpw1, ref=cross_ports1['4'], port=1)

        path = [0]
        path.append(path[-1] - 1j * g_length[1])
        cpw2 = cpw_1.new_cpw(path=np.squeeze(path), a=g_a[0], b=g_b[0], r=r)
        cpw2_2_ports = gmon.combine_device(cpw2, ref=cross_ports2['4'], axis='y', port=1)

    JJ_span2 = [(g_a[1] + 2 * g_b[1]), nanowire_height * 2]
    JJ = JJ_1(zone=JJ_span2,
              nanowire_height=nanowire_height, nanowire_gap=nanowire_gap, nanowire_width=nanowire_width,
              nanowire_extension=nanowire_extension, w_electrode=w_electrode, protection_gap=protection_gap)
    JJ_ports = gmon.combine_device(JJ, ref=cross_ports1['1'], degree=90)

    resonator.combine_device(gmon, ref=cpw2_ports['2'], port=1)

    z = xmon_1.z_1(length=z_length, width=z_width, a=a, b=b, a2=a2, b2=b2)
    z_ports = resonator.combine_device(z, ref=cpw2_ports['2'] + JJ_span[1] / 2 - 1j * (JJ_span2[0] / 2 + z_gap),
                                       degree=90, port=2)

    resonator.add_port(1, 0)
    resonator.add_port(2, cpw2_ports['2'] + cross_ports2['3'])
    resonator.add_port(3, xy_ports['1'])
    resonator.add_port(4, z_ports['1'])

    return resonator


def JJ_1(zone=(24, 8),
         nanowire_height=4, nanowire_gap=0.5,
         nanowire_width=0.2, nanowire_extension=1,
         w_electrode=3, protection_gap=1.5):
    JJ = geo.device()

    poly_0 = [-zone[0] / 2]
    poly_0.append(poly_0[-1] - 1j * zone[1])
    poly_0.append(poly_0[-1] + zone[0])
    poly_0.append(poly_0[-1] + 1j * zone[1])

    width_gap = protection_gap + nanowire_width + nanowire_gap
    height_1 = (zone[1] - nanowire_height) - nanowire_width / 2 - protection_gap

    poly_1 = [width_gap / 2]
    poly_1.append(poly_1[-1] - 1j * height_1)
    poly_1.append(poly_1[-1] + w_electrode)
    poly_1.append(poly_1[-1] + 1j * height_1)

    height_2 = (zone[1] - nanowire_height) + nanowire_width / 2 + nanowire_gap

    poly_2 = [-(width_gap / 2 + w_electrode) - 1j * height_2]
    poly_2.append(-(width_gap / 2 + w_electrode) - 1j * zone[1])
    poly_2.append(-width_gap / 2 - 1j * zone[1])
    poly_2.append(-width_gap / 2 - 1j * height_2)

    poly_4 = geo.poly_hole(poly_0, poly_1)
    poly_4 = geo.poly_hole(poly_4, poly_2)

    JJ.add_geometry('Nb_inv', [poly_4])
    JJ.add_port(1, 0)
    JJ.add_port(2, - 1j * zone[1])

    # JJ
    poly_1 = [-width_gap / 2 - nanowire_extension + 1j * nanowire_width / 2]
    poly_1.append(-width_gap / 2 - nanowire_extension - 1j * nanowire_width / 2)
    poly_1.append((width_gap / 2 - nanowire_gap + nanowire_width / 2 + nanowire_extension) - 1j * nanowire_width / 2)
    poly_1.append((width_gap / 2 - nanowire_gap + nanowire_width / 2 + nanowire_extension) + 1j * nanowire_width / 2)
    poly_1 = np.array(poly_1) - 1j * (zone[1] - nanowire_height)

    JJ.add_geometry('JJ1', [poly_1])

    # poly_2 = [-nanowire_width - 1j * (height_1 - nanowire_extension)]
    # poly_2.append(-nanowire_width - 1j * (nanowire_height + nanowire_width/2 + nanowire_extension))
    # poly_2.append(0 - 1j * (nanowire_height + nanowire_width/2 + nanowire_extension))
    # poly_2.append(0 - 1j * (height_1 - nanowire_extension))
    # poly_2 = np.array(poly_2) + width_gap/2 - nanowire_gap

    poly_2 = [-nanowire_width / 2 - 1j * (height_1 - nanowire_extension)]
    poly_2.append(-nanowire_width / 2 - 1j * (zone[1] - nanowire_height + nanowire_width / 2 + nanowire_extension))
    poly_2.append(nanowire_width / 2 - 1j * (zone[1] - nanowire_height + nanowire_width / 2 + nanowire_extension))
    poly_2.append(nanowire_width / 2 - 1j * (height_1 - nanowire_extension))
    poly_2 = np.array(poly_2) + width_gap / 2 - nanowire_gap - nanowire_width / 2

    JJ.add_geometry('JJ1', [poly_2])

    return JJ

# design = geo.design(name='lambda4_gline', time='250602', logo='QCD')
# resonator = new_resonator()
# design.add_device(resonator)
# design.gen_gds()
