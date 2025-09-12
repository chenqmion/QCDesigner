import sys

# from spectrum_1 import *

# from shapely.geometry import LinearRing, Polygon, MultiPolygon

sys.path.append('../../geometry')

sys.path.append('../../geometry/device')
from bku_link_1 import *
from aux_marker import *
from bku_cpw_1 import *
from lumped_1 import *


def new_lambda4(length_wg=6000, width_wg=600, N=0, length_c=0, gap_c=6, length_stub=100, length_load=100, a=10, b=6,
                r=50):
    lambda4 = device()

    if length_c == 0:
        length_c = width_wg - 2 * r

    cpw_1 = new_cpw(path=[(0, 0), (length_c, 0)], a=a, b=b, r=r)
    cpw_1.terminate_port(1, width=(a + 2 * b), gap=gap_c, degree=180)
    cpw_1_ports = lambda4.combine_device(cpw_1, port=1)

    if N == 0:
        N = int(np.floor(
            ((length_wg - (length_stub + (a / 2 + b)) - length_c - np.pi * r / 2)) / (np.pi * r + (width_wg - 2 * r))))

    length_2 = N * (np.pi * r + (width_wg - 2 * r))

    length_3 = length_wg - (length_stub + (a / 2 + b)) - length_c - length_2

    cpw_2 = cpw_offline(pt_start=(0, 0), length=length_2, width=width_wg, N=N, a=a, b=b, r=r, d_rad=np.pi / 36)
    cpw_2_ports = lambda4.combine_device(cpw_2, ref=cpw_1_ports['2'], port=1)

    cpw_3 = new_cpw(path=[(0, 0), (r, 0), (r, -length_3)], a=a, b=b, r=r)
    if N % 2 == 0:
        cpw_3_ports = lambda4.combine_device(cpw_3, ref=tuple(cpw_2_ports['2']), port=1)
    else:
        cpw_3_ports = lambda4.combine_device(cpw_3, ref=tuple(cpw_2_ports['2']), port=1, axis='y')

    tail_1 = new_joint(length_list=[length_stub, length_load, 0, a / 2 + b], a_list=[a, a, a, a], b_list=[b, b, b, b])
    if N % 2 == 0:
        tail_1_ports = lambda4.combine_device(tail_1, ref=tuple(cpw_3_ports['2']), port=4)
    else:
        tail_1_ports = lambda4.combine_device(tail_1, ref=tuple(cpw_3_ports['2']), port=4, axis='y')

    # %%
    lambda4.add_port(1, (0, 0))
    lambda4.add_port(2, tail_1_ports['2'])

    return lambda4


def new_junction(width_gap=4, height_gap=14,
                 width_nanowire=0.15, length_nanowire=0.6, width_patch=0.3,
                 over_etch=0.5,
                 a=10, b=6):
    junction = device()

    # %% gap
    poly_1 = []
    poly_1.append((-(a / 2 + b), -height_gap / 2))
    poly_1.append((-(a / 2 + b), height_gap / 2))
    poly_1.append((-a / 2, height_gap / 2))
    poly_1.append((-a / 2, -1))
    poly_1.append((-width_gap / 2, -1))
    poly_1.append((-width_gap / 2, -height_gap / 2))

    poly_2 = []
    poly_2.append((-width_gap / 2, -height_gap / 2))
    poly_2.append((-width_gap / 2, height_gap / 2))
    poly_2.append((width_gap / 2, height_gap / 2))
    poly_2.append((width_gap / 2, -height_gap / 2))

    poly_3 = []
    poly_3.append((width_gap / 2, 1))
    poly_3.append((width_gap / 2, height_gap / 2))
    poly_3.append(((a / 2 + b), height_gap / 2))
    poly_3.append(((a / 2 + b), 1))
    junction.add_geometry('Nb_inv', [poly_1, poly_2, poly_3])

    # %% nanowire
    poly_1 = []
    poly_1.append((-width_nanowire / 2, -length_nanowire / 2))
    poly_1.append((-width_nanowire / 2, length_nanowire / 2))
    poly_1.append((width_nanowire / 2, length_nanowire / 2))
    poly_1.append((width_nanowire / 2, -length_nanowire / 2))
    junction.add_geometry('EBL_1', [poly_1])

    poly_1 = []
    poly_1.append((-width_nanowire / 2, length_nanowire / 2))
    poly_1.append((-width_nanowire / 2, length_nanowire / 2 + width_patch + over_etch))
    poly_1.append((width_nanowire / 2, length_nanowire / 2 + width_patch + over_etch))
    poly_1.append((width_nanowire / 2, length_nanowire / 2))

    poly_2 = ope_reflect(poly_1, axis='x', value=0)
    junction.add_geometry('EBL_1', [poly_1, poly_2])

    poly_1 = []
    poly_1.append((-width_nanowire / 2, length_nanowire / 2 + width_patch + over_etch))
    poly_1.append((-width_nanowire / 2, length_nanowire / 2 + width_patch + 2 * over_etch))
    poly_1.append((width_nanowire / 2, length_nanowire / 2 + width_patch + 2 * over_etch))
    poly_1.append((width_nanowire / 2, length_nanowire / 2 + width_patch + over_etch))

    poly_2 = ope_reflect(poly_1, axis='x', value=0)
    junction.add_geometry('EBL_1_ghost', [poly_1, poly_2])

    # %% patch
    poly_1 = []
    poly_1.append((-width_gap / 2, length_nanowire / 2))
    poly_1.append((-width_gap / 2, length_nanowire / 2 + width_patch))
    poly_1.append((width_nanowire / 2, length_nanowire / 2 + width_patch))
    poly_1.append((width_nanowire / 2, length_nanowire / 2))

    poly_2 = ope_rotate(poly_1, origin=(0, 0), degree=180)
    junction.add_geometry('EBL_1', [poly_1, poly_2])

    poly_1 = []
    poly_1.append((-width_gap / 2 - over_etch, length_nanowire / 2))
    poly_1.append((-width_gap / 2 - over_etch, length_nanowire / 2 + width_patch))
    poly_1.append((-width_gap / 2, length_nanowire / 2 + width_patch))
    poly_1.append((-width_gap / 2, length_nanowire / 2))

    poly_2 = ope_rotate(poly_1, origin=(0, 0), degree=180)
    junction.add_geometry('EBL_1', [poly_1, poly_2])

    poly_1 = []
    poly_1.append((width_nanowire / 2, length_nanowire / 2))
    poly_1.append((width_nanowire / 2, length_nanowire / 2 + width_patch))
    poly_1.append((width_nanowire / 2 + over_etch, length_nanowire / 2 + width_patch))
    poly_1.append((width_nanowire / 2 + over_etch, length_nanowire / 2))

    poly_2 = ope_rotate(poly_1, origin=(0, 0), degree=180)
    junction.add_geometry('EBL_1', [poly_1, poly_2])

    poly_1 = []
    poly_1.append((-width_gap / 2 - 2 * over_etch, length_nanowire / 2))
    poly_1.append((-width_gap / 2 - 2 * over_etch, length_nanowire / 2 + width_patch))
    poly_1.append((-width_gap / 2 - over_etch, length_nanowire / 2 + width_patch))
    poly_1.append((-width_gap / 2 - over_etch, length_nanowire / 2))
    poly_2 = ope_rotate(poly_1, origin=(0, 0), degree=180)

    poly_3 = []
    poly_3.append((width_nanowire / 2 + over_etch, length_nanowire / 2))
    poly_3.append((width_nanowire / 2 + over_etch, length_nanowire / 2 + width_patch))
    poly_3.append((width_nanowire / 2 + 2 * over_etch, length_nanowire / 2 + width_patch))
    poly_3.append((width_nanowire / 2 + 2 * over_etch, length_nanowire / 2))
    poly_4 = ope_rotate(poly_3, origin=(0, 0), degree=180)

    junction.add_geometry('EBL_1_ghost', [poly_1, poly_2, poly_3, poly_4])

    junction.add_port(1, (0, height_gap / 2))
    junction.add_port(2, (0, -height_gap / 2))

    return junction


def new_heater(length_wg=6000, width_wg=600, N=0, length_c=0, gap_c=6, length_stub=100, length_load=100,
               width_gap=4, height_gap=14, width_nanowire=0.15, length_nanowire=0.6, width_patch=0.3, over_etch=0.5,
               a=10, b=6, r=50):
    heater = device()

    lambda4 = new_lambda4(length_wg=length_wg, width_wg=width_wg, N=N, length_c=length_c, gap_c=gap_c,
                          length_stub=length_stub, length_load=length_load - 1, a=a, b=b, r=r)
    lambda4_ports = heater.combine_device(lambda4, port=1)

    junction_1 = new_junction(width_gap=width_gap, height_gap=height_gap,
                              width_nanowire=width_nanowire, length_nanowire=length_nanowire, width_patch=width_patch,
                              over_etch=over_etch,
                              a=a, b=b)
    ref_junction = np.add(lambda4_ports['2'], [0, height_gap / 2 - 1])
    junction_1_ports = heater.combine_device(junction_1, ref=ref_junction, port=1)

    # %%
    heater.add_port(1, (0, 0))

    return heater
