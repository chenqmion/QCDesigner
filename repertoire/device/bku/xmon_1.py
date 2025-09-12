import sys

import numpy as np

sys.path.append('../')
import geometry_class as geo

import junction_1


def new_xmon(  # cross
        x_angle=[0, 90, 180, 270], x_length=(130, 130, 130, 130), x_a_list=(8, 8, 8, 8), x_b_list=(8, 8, 8, 8),
        x_cap=(8, 8, 8, 0),
        # readout resonator
        ro_angle=90,
        cap_width=[None, 80], cap_gap=[6, 6], cap_length=[50, 20], ro_gap=5,
        ro_length=5070, ro_height=(1000, 200), ro_width=(500, 200), ro_mode='compact',
        # xy
        xy_angle=None, xy_length=(10, 10, 50), xy_cap=3, xy_gap=10,
        # z
        z_angle=None, z_length=(10, 10, 50), z_width=(5, 20), z_gap=5,
        # general
        a=10, b=6, r=50, d_rad=np.pi / 36, a2=5, b2=3):
    xmon = geo.device()

    cross = cross_1(angle=x_angle, length=x_length, a_list=x_a_list, b_list=x_b_list, cap=x_cap)
    cross_ports = xmon.combine_device(cross, ref=0, port=1)

    # xy
    if xy_angle != None:
        idx = np.where((np.array(x_angle) % (2 * np.pi)) == (xy_angle % (2 * np.pi)))
        xy = xy_1(length=xy_length, cap=xy_cap, a=a, b=b, a2=a2, b2=b2)
        xy_ports = xmon.combine_device(xy, ref=cross_ports[str(np.squeeze(idx) + 1)] - (x_cap[2] + xy_cap + xy_gap),
                                       port=2)

    # z
    JJ = SQUID_1(zone=(x_a_list[3] + 2 * x_b_list[3], x_cap[1]),
                 nanowire_span=6, nanowire_height=x_cap[1] / 2, nanowire_gap=0.5,
                 nanowire_width=0.2, nanowire_extension=1,
                 w_electrode=3, protection_gap=1.5)

    if z_angle == None:
        JJ_ports = xmon.combine_device(JJ, ref=cross_ports['4'], port=1)
    else:
        idx = np.where((np.array(x_angle) % (2 * np.pi)) == (z_angle % (2 * np.pi)))
        JJ_ports = xmon.combine_device(JJ, ref=cross_ports[str(np.squeeze(idx) + 1)], port=1)

        z = z_1(length=z_length, width=z_width, a=a, b=b, a2=a2, b2=b2)
        z_ports = xmon.combine_device(z, ref=JJ_ports['2'] - 1j * z_gap, degree=90, port=2)

    # readout
    if ro_angle != None:
        idx = np.squeeze(np.where((np.array(x_angle) % (2 * np.pi)) == (ro_angle % (2 * np.pi))))
        cap_width[0] = x_a_list[idx] + 2 * x_b_list[idx] + 2 * cap_gap[0] + 2 * ro_gap
        cap = cap_1(width=cap_width, gap=cap_gap, length=cap_length, a=a, b=b)

        ref_cap = cross_ports[str(np.squeeze(idx) + 1)] + (cap_gap[0] + x_cap[idx] + ro_gap) * np.exp(
            1j * ro_angle * np.pi / 180)

        cap_ports = xmon.combine_device(cap, ref=ref_cap, port=1, degree=ro_angle - 90)

        if ro_angle == 180:
            path = [0]
            path.append(ro_width[1] * np.exp(1j * ro_angle * np.pi / 180))
            path.append(path[-1] + r * np.exp(1j * (ro_angle - 90) * np.pi / 180))

            cpw0 = cpw_1.new_cpw(path=np.squeeze(path),
                                 a=a, b=b, r=r)
            cpw_ports = xmon.combine_device(cpw0, ref=cap_ports['2'], port=1)
            ref_cpw = cpw_ports['2']
            len_cpw = ro_length - (ro_width[1] - r + np.pi * r)
        else:
            ref_cpw = cap_ports['2']
            len_cpw = ro_length

        cpw = resonator_readout_1(pt_start=0, length=len_cpw, height=ro_height, width=ro_width,
                                  a=a, b=b, r=r, d_rad=d_rad,
                                  mode=ro_mode)
        cpw_ports = xmon.combine_device(cpw, ref=ref_cpw, port=1, axis='y')

    xmon.add_port(1, cross_ports['1'])
    if ro_angle != None:
        xmon.add_port(2, cpw_ports['2'])
    else:
        xmon.add_port(3, cross_ports['2'])

    if xy_angle != None:
        xmon.add_port(3, xy_ports['1'])
    else:
        xmon.add_port(3, cross_ports['1'])

    if z_angle != None:
        xmon.add_port(4, z_ports['1'])
    else:
        xmon.add_port(4, JJ_ports['2'])

    return xmon


def resonator_readout_1(pt_start=0,
                        length=5070, height=(1000, 200), width=(500, 200), N=4,
                        a=10, b=6, r=50, d_rad=np.pi / 36,
                        mode='compact'):
    # PRL 111, 080502 (2013)

    path = [pt_start]
    path.append(pt_start + 1j * height[0])
    path.append(path[-1] - (width[0] + width[1]))
    path.append(path[-1] - 1j * height[1])
    path.append(path[-1] + width[0] - r)

    cpw = cpw_1.new_cpw(path, a=a, b=b, r=r)
    cpw.add_port(1, path[0])
    cpw.add_port(2, (path[1] + path[2]) / 2)

    length_1 = (height[0] + height[1] - 3 * r) + (2 * width[0] + width[1] - 3 * r) + 3 * np.pi * r / 2
    length_2 = length - length_1

    cpw_2 = cpw_meander_1.cpw_offline(pt_start=0,
                                      length=length_2, width=width[0], N=N,
                                      a=a, b=b, r=r, d_rad=d_rad,
                                      mode=mode)

    new_ports = cpw.combine_device(cpw_2, ref=path[-1])

    # cpw.add_port(2, new_ports['2'])

    return cpw


def cross_1(angle=(0, 90, 180, 270), length=(130, 130, 130, 130), a_list=(8, 8, 8, 8), b_list=(8, 8, 8, 8),
            cap=(8, 8, 8, 8)):
    cross = geo.device()

    path_inner = []
    path_outer = []
    for num_angle, val_angle in enumerate(angle):
        if num_angle == len(angle) - 1:
            num_angle2 = 0
        else:
            num_angle2 = num_angle + 1

        for num_1 in range(2):
            x0 = (length[num_angle] + num_1 * cap[num_angle]) * np.exp(1j * angle[num_angle] * np.pi / 180)
            y01 = (a_list[num_angle] / 2 + num_1 * b_list[num_angle]) * np.exp(
                1j * (angle[num_angle] + 90) * np.pi / 180)
            y02 = x0 + y01

            if num_1 == 0:
                cross.add_port(num_angle + 1, x0)

            x1 = (length[num_angle2] + num_1 * cap[num_angle2]) * np.exp(1j * angle[num_angle2] * np.pi / 180)
            y11 = (a_list[num_angle2] / 2 + num_1 * b_list[num_angle2]) * np.exp(
                1j * (angle[num_angle2] - 90) * np.pi / 180)
            y12 = x1 + y11

            # find intersect
            a0 = (y01 - y02).imag
            b0 = (y02 - y01).real
            c0 = y01.real * y02.imag - y02.real * y01.imag

            a1 = (y11 - y12).imag
            b1 = (y12 - y11).real
            c1 = y11.real * y12.imag - y12.real * y11.imag

            d = a0 * b1 - a1 * b0
            xc = (b0 * c1 - b1 * c0) / d
            yc = (a1 * c0 - a0 * c1) / d

            if num_1 == 0:
                path_inner += [y02, xc + 1j * yc, y12]
            else:
                path_outer += [y02, xc + 1j * yc, y12]

    poly1 = geo.poly_hole(path_outer, path_inner)
    cross.add_geometry('Nb_inv', [poly1])

    return cross


def cap_1(width=(42, 100), gap=(6, 12), length=(100, 50), a=10, b=6):
    cap = geo.device()

    poly1 = [-(width[1] / 2 + gap[1]) - 1j * (length[0] + gap[0])]
    poly1.append(-(width[1] / 2 + gap[1]))
    poly1.append(-width[1] / 2)
    poly1.append(-width[1] / 2 - 1j * length[0])
    poly1.append(-width[0] / 2 - 1j * length[0])
    poly1.append(-width[0] / 2)
    poly1.append(0)
    poly1.append(- 1j * gap[0])
    poly1.append(-(width[0] / 2 - gap[0]) - 1j * gap[0])
    poly1.append(-(width[0] / 2 - gap[0]) - 1j * (length[0] + gap[0]))

    poly2 = geo.poly_reflect(poly1, axis='y', value=0)
    cap.add_geometry('Nb_inv', [poly1, poly2])

    # taper = link_1.new_taper(length=length[1], a=width[1], b=gap[1], a2=a, b2=b)
    # taper_ports = cap.combine_device(taper, ref= 0, degree=90, port=1)

    poly1 = [-(width[1] / 2 + gap[1])]
    poly1.append(poly1[-1] + 1j * (length[1] + gap[1]))
    poly1.append(-a / 2 + 1j * poly1[-1].imag)
    poly1.append(poly1[-1] - 1j * gap[1])
    poly1.append(-(width[1] / 2) + 1j * length[1])
    poly1.append(-width[1] / 2)

    poly2 = geo.poly_reflect(poly1, axis='y', value=0)
    cap.add_geometry('Nb_inv', [poly1, poly2])

    cap.add_port(1, 0)
    cap.add_port(2, 1j * (length[1] + gap[1]))

    return cap


def xy_1(length=(10, 10, 50), cap=3, a=10, b=6, a2=5, b2=3):
    xy = geo.device()
    cpw1 = cpw_1.cpw_straight(0, length[0], a=a, b=b)
    cpw2 = cpw_1.cpw_straight(length[0] + length[1], length[0] + length[1] + length[2], a=a2, b=b2)

    xy.add_geometry('Nb_inv', cpw1 + cpw2)

    taper = link_1.new_taper(length=length[1], a=a, b=b, a2=a2, b2=b2)
    taper_ports = xy.combine_device(taper, ref=length[0], port=1)

    xy.add_port(1, 0)
    xy.add_port(2, length[0] + length[1] + length[2])

    xy.terminate_port(2, width=(a2 + 2 * b2), gap=cap, degree=0, layer='Nb_inv')

    return xy


def z_1(length=(10, 10, 50), width=(3, 10), a=10, b=6, a2=3, b2=2):
    z = geo.device()
    cpw1 = cpw_1.cpw_straight(0, length[0], a=a, b=b)
    cpw2 = cpw_1.cpw_straight(length[0] + length[1], length[0] + length[1] + length[2], a=a2, b=b2)

    z.add_geometry('Nb_inv', cpw1 + cpw2)

    taper = link_1.new_taper(length=length[1], a=a, b=b, a2=a2, b2=b2)
    taper_ports = z.combine_device(taper, ref=length[0], port=1)

    poly_1 = [1j * a2 / 2]
    poly_1.append(1j * (a2 / 2 + width[0]))
    poly_1.append(b2 + 1j * (a2 / 2 + width[0]))
    poly_1.append(b2 + 1j * a2 / 2)

    poly_2 = [a2 + b2 - 1j * width[1] / 2]
    poly_2.append(a2 + b2 + 1j * width[1] / 2)
    poly_2.append(a2 + 2 * b2 + 1j * width[1] / 2)
    poly_2.append(a2 + 2 * b2 - 1j * width[1] / 2)

    z.add_geometry('Nb_inv', [poly_1, poly_2], ref=length[0] + length[1] + length[2] - b2)

    z.add_port(1, 0)
    z.add_port(2, length[0] + length[1] + length[2] + (a2 + b2))

    return z


# %% JJ
def SQUID_1(zone=(24, 8),
            nanowire_span=6, nanowire_height=4, nanowire_gap=0.5,
            nanowire_width=0.2, nanowire_extension=1,
            w_electrode=3, protection_gap=1.5):
    JJ = junction_1.new_cross(length_list=[100, 100, 100, 100], a_list=[10, 10], layer=['AuPd', 'Al'],
                              shadow={'da_list': [0, 0], 'length_list': [0.5, 0.5, 0.5, 0.5]})

    SQUID = geo.device()

    poly_0 = [-zone[0] / 2]
    poly_0.append(poly_0[-1] - 1j * zone[1])
    poly_0.append(poly_0[-1] + zone[0])
    poly_0.append(poly_0[-1] + 1j * zone[1])

    width_1 = nanowire_span - nanowire_width - 2 * nanowire_gap
    height_1 = zone[1] - nanowire_height - nanowire_width / 2 - protection_gap

    poly_1 = [-width_1 / 2]
    poly_1.append(-width_1 / 2 - 1j * height_1)
    poly_1.append(width_1 / 2 - 1j * height_1)
    poly_1.append(width_1 / 2)

    width_2 = nanowire_span + nanowire_width + 2 * protection_gap
    height_2 = zone[1] - nanowire_height + nanowire_width / 2 + nanowire_gap

    poly_2 = [-(width_2 / 2 + w_electrode) - 1j * height_2]
    poly_2.append(-(width_2 / 2 + w_electrode) - 1j * zone[1])
    poly_2.append(-width_2 / 2 - 1j * zone[1])
    poly_2.append(-width_2 / 2 - 1j * height_2)

    poly_3 = geo.poly_reflect(poly_2, axis='y', value=0)

    poly_4 = geo.poly_hole(poly_0, poly_1)
    poly_4 = geo.poly_hole(poly_4, poly_2)
    poly_4 = geo.poly_hole(poly_4, poly_3[::-1])

    SQUID.add_geometry('Nb_inv', [poly_4])
    SQUID.add_port(1, 0)
    SQUID.add_port(2, - 1j * zone[1])

    # JJ
    poly_1 = [-width_2 / 2 - nanowire_extension + 1j * nanowire_width / 2]
    poly_1.append(-width_2 / 2 - nanowire_extension - 1j * nanowire_width / 2)
    poly_1.append((- nanowire_span / 2 + nanowire_width / 2 + nanowire_extension) - 1j * nanowire_width / 2)
    poly_1.append((- nanowire_span / 2 + nanowire_width / 2 + nanowire_extension) + 1j * nanowire_width / 2)
    poly_1 = np.array(poly_1) - 1j * (zone[1] - nanowire_height)

    poly_12 = geo.poly_reflect(poly_1, axis='y', value=0)

    SQUID.add_geometry('JJ1', [poly_1, poly_12])

    poly_2 = [-nanowire_width / 2 - 1j * (height_1 - nanowire_extension)]
    poly_2.append(-nanowire_width / 2 - 1j * (zone[1] - nanowire_height + nanowire_width / 2 + nanowire_extension))
    poly_2.append(nanowire_width / 2 - 1j * (zone[1] - nanowire_height + nanowire_width / 2 + nanowire_extension))
    poly_2.append(nanowire_width / 2 - 1j * (height_1 - nanowire_extension))
    poly_2 = np.array(poly_2) - nanowire_span / 2

    poly_22 = geo.poly_reflect(poly_2, axis='y', value=0)

    SQUID.add_geometry('JJ1', [poly_2, poly_22])

    return SQUID

# %%
# xmon = new_xmon()
# design = geo.design(name='resonator_readout_1', time='250602', logo='QCD')
# design.add_device(xmon)
# design.gen_gds()
