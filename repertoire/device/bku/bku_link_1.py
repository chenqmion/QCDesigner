import sys

sys.path.append('../')

from bku_cpw_1 import *


def new_taper(length=50, a=10, b=6, a2=10, b2=6):
    taper = geo.device()

    poly_1 = []
    poly_1.append(1j * a / 2)
    poly_1.append(1j * (a / 2 + b))
    poly_1.append(length + 1j * (a2 / 2 + b2))
    poly_1.append(length + 1j * a2 / 2)

    poly_2 = geo.poly_reflect(poly_1, axis='x', value=0)
    taper.add_geometry('Nb_inv', [poly_1, poly_2])

    taper.add_port(1, 0)
    taper.add_port(2, length)

    return taper


def new_joint(length_list=[100, 100, 100, 100], a_list=[10, 10, 10, 10], b_list=[6, 6, 6, 6]):
    joint = device()

    for num_length, val_length in enumerate(length_list):
        if val_length == 0:
            a_list[num_length] = 0
            b_list[num_length] = 0

    x_off = np.max(np.array(a_list[1::2]) + 2 * np.array(b_list[1::2])) / 2
    y_off = np.max(np.array(a_list[0::2]) + 2 * np.array(b_list[0::2])) / 2
    x_center = length_list[0]

    pt_1 = (x_center - x_off, 0)
    pt_2 = (x_center, -y_off)
    pt_3 = (x_center + x_off, 0)
    pt_4 = (x_center, y_off)

    # %% waveguides
    joint.add_port(1, (0, 0))
    if length_list[0] != 0:
        cpw_1 = new_cpw(path=[(0, 0), pt_1], a=a_list[0], b=b_list[0])
        joint.add_geometry('Nb_inv', cpw_1.geometry_list[0])

    if length_list[1] != 0:
        cpw_2 = new_cpw(path=[pt_2, (x_center, -length_list[1])], a=a_list[1], b=b_list[1])
        joint.add_geometry('Nb_inv', cpw_2.geometry_list[0])
        joint.add_port(2, (x_center, -length_list[1]))

    if length_list[2] != 0:
        cpw_3 = new_cpw(path=[pt_3, (x_center + length_list[2], 0)], a=a_list[2], b=b_list[2])
        joint.add_geometry('Nb_inv', cpw_3.geometry_list[0])
        joint.add_port(3, (x_center + length_list[2], 0))

    if length_list[3] != 0:
        cpw_4 = new_cpw(path=[pt_4, (x_center, length_list[3])], a=a_list[3], b=b_list[3])
        joint.add_geometry('Nb_inv', cpw_4.geometry_list[0])
        joint.add_port(4, (x_center, length_list[3]))

    # %% patches
    patch_geometry = []

    if length_list[1] != 0:  # 0-1
        poly_12 = [(pt_1[0], -(a_list[0] + 2 * b_list[0]) / 2)]
        poly_12.append((pt_1[0], -a_list[0] / 2))
        poly_12.append((pt_2[0] - a_list[1] / 2, -a_list[0] / 2))
        poly_12.append((pt_2[0] - a_list[1] / 2, -(a_list[0] + 2 * b_list[0]) / 2))
        patch_geometry.append(poly_12)

        poly_21 = [(pt_2[0] - (a_list[1] + 2 * b_list[1]) / 2, pt_2[1])]
        poly_21.append((pt_2[0] - (a_list[1] + 2 * b_list[1]) / 2, -a_list[0] / 2))
        poly_21.append((pt_2[0] - a_list[1] / 2, -a_list[0] / 2))
        poly_21.append((pt_2[0] - a_list[1] / 2, pt_2[1]))
        patch_geometry.append(poly_21)
    else:
        if length_list[2] != 0:  # 0-2
            poly_13 = [(pt_1[0], -(a_list[0] + 2 * b_list[0]) / 2)]
            poly_13.append((pt_1[0], -a_list[0] / 2))
            poly_13.append((pt_3[0], -a_list[2] / 2))
            poly_13.append((pt_3[0], -(a_list[2] + 2 * b_list[2]) / 2))
            patch_geometry.append(poly_13)
        else:  # 0-3
            poly_14 = [(pt_1[0], -(a_list[0] + 2 * b_list[0]) / 2)]
            poly_14.append((pt_1[0], -a_list[0] / 2))
            poly_14.append((pt_4[0] + a_list[3] / 2, -a_list[0] / 2))
            poly_14.append((pt_4[0] + a_list[3] / 2, pt_4[1]))
            poly_14.append((pt_4[0] + (a_list[3] + 2 * b_list[3]) / 2, pt_4[1]))
            poly_14.append((pt_4[0] + (a_list[3] + 2 * b_list[3]) / 2, -a_list[0] / 2))
            poly_14.append((pt_4[0] + (a_list[3] + 2 * b_list[3]) / 2, -(a_list[0] + 2 * b_list[0]) / 2))
            patch_geometry.append(poly_14)

    if length_list[1] != 0:
        if length_list[2] != 0:  # 1-2
            poly_23 = [(pt_2[0] + a_list[1] / 2, pt_2[1])]
            poly_23.append((pt_2[0] + a_list[1] / 2, -a_list[2] / 2))
            poly_23.append((pt_2[0] + (a_list[1] + 2 * b_list[1]) / 2, -a_list[2] / 2))
            poly_23.append((pt_2[0] + (a_list[1] + 2 * b_list[1]) / 2, pt_2[1]))
            patch_geometry.append(poly_23)

            poly_32 = [(pt_2[0] + a_list[1] / 2, -(a_list[2] + 2 * b_list[2]) / 2)]
            poly_32.append((pt_2[0] + a_list[1] / 2, -a_list[2] / 2))
            poly_32.append((pt_3[0], -a_list[2] / 2))
            poly_32.append((pt_3[0], -(a_list[2] + 2 * b_list[2]) / 2))
            patch_geometry.append(poly_32)
        else:
            if length_list[3] != 0:  # 1-3
                poly_23 = [(pt_2[0] + a_list[1] / 2, pt_2[1])]
                poly_23.append((pt_4[0] + a_list[3] / 2, pt_4[1]))
                poly_23.append((pt_4[0] + (a_list[3] + 2 * b_list[3]) / 2, pt_4[1]))
                poly_23.append((pt_2[0] + (a_list[1] + 2 * b_list[1]) / 2, pt_2[1]))
                patch_geometry.append(poly_23)
            else:  # 1-0
                poly_21 = [(pt_2[0] + a_list[1] / 2, pt_2[1])]
                poly_21.append((pt_2[0] + a_list[1] / 2, a_list[0] / 2))
                poly_21.append((pt_1[0], a_list[0] / 2))
                poly_21.append((pt_1[0], (a_list[0] + 2 * b_list[0]) / 2))
                poly_21.append((pt_2[0] + a_list[1] / 2, (a_list[0] + 2 * b_list[0]) / 2))
                poly_21.append((pt_2[0] + (a_list[1] + 2 * b_list[1]) / 2, (a_list[0] + 2 * b_list[0]) / 2))
                poly_21.append((pt_2[0] + (a_list[1] + 2 * b_list[1]) / 2, pt_2[1]))
                patch_geometry.append(poly_21)

    if length_list[2] != 0:
        if length_list[3] != 0:
            poly_34 = [(pt_4[0] + a_list[3] / 2, a_list[2] / 2)]
            poly_34.append((pt_4[0] + a_list[3] / 2, (a_list[2] + 2 * b_list[2]) / 2))
            poly_34.append((pt_3[0], (a_list[2] + 2 * b_list[2]) / 2))
            poly_34.append((pt_3[0], a_list[2] / 2))
            patch_geometry.append(poly_34)

            poly_43 = [(pt_4[0] + (a_list[3] + 2 * b_list[3]) / 2, a_list[2] / 2)]
            poly_43.append((pt_4[0] + (a_list[3] + 2 * b_list[3]) / 2, pt_4[1]))
            poly_43.append((pt_4[0] + a_list[3] / 2, pt_4[1]))
            poly_43.append((pt_4[0] + a_list[3] / 2, a_list[2] / 2))
            patch_geometry.append(poly_43)
        else:
            poly_31 = [(pt_1[0], a_list[0] / 2)]
            poly_31.append((pt_1[0], (a_list[0] + 2 * b_list[0]) / 2))
            poly_31.append((pt_3[0], (a_list[2] + 2 * b_list[2]) / 2))
            poly_31.append((pt_3[0], a_list[2] / 2))
            patch_geometry.append(poly_31)

    if length_list[3] != 0:
        poly_14 = [(pt_1[0], a_list[0] / 2)]
        poly_14.append((pt_1[0], (a_list[0] + 2 * b_list[0]) / 2))
        poly_14.append((pt_4[0] - a_list[3] / 2, (a_list[0] + 2 * b_list[0]) / 2))
        poly_14.append((pt_4[0] - a_list[3] / 2, a_list[0] / 2))
        patch_geometry.append(poly_14)

        poly_41 = [(pt_4[0] - (a_list[3] + 2 * b_list[3]) / 2, a_list[0] / 2)]
        poly_41.append((pt_4[0] - (a_list[3] + 2 * b_list[3]) / 2, pt_4[1]))
        poly_41.append((pt_4[0] - a_list[3] / 2, pt_4[1]))
        poly_41.append((pt_4[0] - a_list[3] / 2, a_list[0] / 2))
        patch_geometry.append(poly_41)

    joint.add_geometry('Nb_inv', patch_geometry)

    return joint
