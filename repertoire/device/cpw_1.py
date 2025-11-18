import numpy as np
import scipy as sci

import datetime
import sys
import os

today = str(datetime.date.today()).split('-')
time_stamp = today[0][-2:] + today[1] + today[2]
device_name = os.path.basename(__file__)[:-3]

sys.path.append('../')
from class_device import device
from class_chip import chip
import aux_poly

#%% design
def new_device(
        path=[0, 1000, 1500 - 500j, 1000 - 1000j, 0 - 1000j, -1000 - 1000j, -500 - 1500j, -1000 - 2000j, 0 - 2000j],
        a=10, b=6, r=50, d_rad=np.pi / 36, layer='Nv_inv'):
    path = np.array(path, dtype=complex)
    idx_keep = (np.diff(path) != 0 + 0j)
    idx_keep = np.insert(idx_keep, [0], [True])
    path = path[idx_keep]

    cpw_1 = device()

    direction_list = np.sign(np.diff(path))
    idx_keep = (np.abs(np.diff(direction_list)) >= 1e-3)
    idx_keep = np.insert(idx_keep, [0, len(idx_keep)], [True, True])
    path = path[idx_keep]

    print(np.diff(direction_list))

    start_list = np.array(path)[:-2]
    mid_list = np.array(path)[1:-1]
    stop_list = np.array(path)[2:]

    cpw_geometry = []

    path2 = [path[0]]
    for x0, x1, x2 in zip(start_list, mid_list, stop_list):
        d0 = x0 - x1
        d1 = x2 - x1

        dx_0 = np.sign(d0.imag - 1j * d0.real)
        if np.real(np.vdot(dx_0, d1)) < 0:
            dx_0 = -dx_0

        y01 = x0 + r * dx_0
        y02 = x1 + r * dx_0

        a0 = (y01 - y02).imag
        b0 = (y02 - y01).real
        c0 = y01.real * y02.imag - y02.real * y01.imag

        dx_1 = np.sign(d1.imag - 1j * d1.real)
        if np.real(np.vdot(dx_1, d0)) < 0:
            dx_1 = -dx_1

        y11 = x1 + r * dx_1
        y12 = x2 + r * dx_1

        a1 = (y11 - y12).imag
        b1 = (y12 - y11).real
        c1 = y11.real * y12.imag - y12.real * y11.imag

        d = a0 * b1 - a1 * b0
        xc = (b0 * c1 - b1 * c0) / d
        yc = (a1 * c0 - a0 * c1) / d

        ph_0 = np.angle(-dx_0)
        ph_1 = np.angle(-dx_1)
        N = int(np.abs((ph_1 - ph_0) / (np.pi / 36)))

        ph_list = np.linspace(ph_0, ph_1, N)
        curve_1 = (xc + 1j * yc) + r * np.exp(1j * ph_list)

        poly_1 = cpw_straight(path2[-1], curve_1[0], a=a, b=b)
        cpw_geometry += poly_1

        poly_2 = cpw_curve(curve_1[0], (xc + 1j * yc), rad=(ph_1 - ph_0), a=a, b=b, d_rad=d_rad)
        cpw_geometry += poly_2

        path2 += list(curve_1)

    poly_1 = cpw_straight(path2[-1], path[-1], a=a, b=b)
    cpw_geometry += poly_1
    path2.append(path[-1])

    cpw_1.add_geometry(layer, cpw_geometry)
    cpw_1.add_port('1', path[0], np.angle(path[0]-path[1])*180/np.pi)
    cpw_1.add_port('2', path[-1], np.angle(path[-1]-path[-2])*180/np.pi)

    return cpw_1

def cpw_straight(pt_start, pt_stop, a=10, b=6):
    d0 = pt_stop - pt_start
    dx_0 = np.sign(d0.imag - 1j * d0.real)

    poly_1 = []
    poly_1.append(pt_start + dx_0 * a / 2)
    poly_1.append(pt_start + dx_0 * (a / 2 + b))
    poly_1.append(pt_stop + dx_0 * (a / 2 + b))
    poly_1.append(pt_stop + dx_0 * (a / 2))

    poly_2 = []
    poly_2.append(pt_start - dx_0 * a / 2)
    poly_2.append(pt_start - dx_0 * (a / 2 + b))
    poly_2.append(pt_stop - dx_0 * (a / 2 + b))
    poly_2.append(pt_stop - dx_0 * (a / 2))

    cpw_geometry = [poly_1, poly_2]
    return cpw_geometry


def cpw_curve(pt_start, pt_ori, rad, a=10, b=6, d_rad=np.pi / 36):
    vec_1 = pt_start - pt_ori
    rad_1 = np.angle(vec_1)

    if np.abs(rad) > np.pi:
        rad = rad - np.sign(rad) * 2 * np.pi

    rad_2 = rad_1 + rad

    r = np.abs(vec_1)
    rad_list = np.arange(rad_1, rad_2, np.sign(rad) * d_rad)
    rad_list = np.append(rad_list, rad_2)

    poly_1 = (r + a / 2 + b) * np.exp(1j * rad_list)
    poly_2 = (r + a / 2) * np.exp(1j * rad_list[::-1])

    poly_1 = list(poly_1 + pt_ori)
    poly_1 += list(poly_2 + pt_ori)
    cpw_geometry = [poly_1]

    poly_2 = (r - a / 2) * np.exp(1j * rad_list)
    poly_1 = (r - a / 2 - b) * np.exp(1j * rad_list[::-1])

    poly_2 = list(poly_2 + pt_ori)
    poly_2 += list(poly_1 + pt_ori)
    cpw_geometry.append(poly_2)

    return cpw_geometry

#%% example
path = [0.00000000e+00 + 0.j, 100+100j, 200+100j, 300+0j]

x = new_device(path=path)

chip_1 = chip(name=device_name,
              time=time_stamp,
              logo='QCD',
              die_size=(15e3, 15e3),
              chip_size=(10e3, 10e3),
              trap_size=(20, 100))
chip_1.combine_device(x, ref=5e3 * (1 + 1j), degree=0, axis='none', port='1')
chip_1.gen_gds(marker=True, flux_trap=True, set_zero=True)
