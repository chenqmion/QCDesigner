import sys

import gdsfactory as gf
import numpy as np

sys.path.append('../')
# from class_chip import design

import aux_poly

def decorator(die_size=(15e3, 15e3),
              chip_size=(10e3, 10e3)
              ):
    geometry_1 = []

    poly_1 = []
    poly_1.append(-100 - 100j)
    poly_1.append(-100 + 1000j)
    poly_1.append(100 + 1000j)
    poly_1.append(100 + 100j)
    poly_1.append(1000 + 100j)
    poly_1.append(1000 - 100j)

    poly_1 = np.array(poly_1) + 500 * (-1 - 1j)
    geometry_1.append(poly_1)

    poly_2 = []
    poly_2.append(-100)
    poly_2.append(-100 + 1000j)
    poly_2.append(100 + 1000j)
    poly_2.append(100)

    for num_1 in range(3):
        poly_2_1 = np.array(poly_2) + 1j * (chip_size[1] - die_size[1]) / 2 + num_1 * chip_size[0] / 2
        poly_2_2 = aux_poly.reflect(poly_2_1, axis='x', value=chip_size[1] / 2)

        poly_2_3 = np.array(poly_2) * np.exp(-1j * np.pi / 2) + (chip_size[0] - die_size[0]) / 2 + 1j * num_1 * \
                   chip_size[1] / 2
        poly_2_4 = aux_poly.reflect(poly_2_3, axis='y', value=chip_size[0] / 2)

        geometry_1 += [poly_2_1, poly_2_2, poly_2_3, poly_2_4]

    return geometry_1


def text(str_text,
         size=3e2):
    text_geometry = []

    x1 = 0
    for str_word in str_text:
        poly_name = gf.components.text(str_word, size, (x1, 0), layer=0)

        for poly in poly_name.get_polygons_points()[0]:
            text_geometry.append(np.array(poly)[:, 0] + 1j * np.array(poly)[:, 1])

        xm = [np.max(val.real) for val in text_geometry]
        x1 = np.max(xm)

    text_geometry2 = [val_poly - (x1 + 1j * size) / 2 for val_poly in text_geometry]

    return text_geometry2


def marker(layer_count=3,
           chip_size=(10e3, 10e3)
           ):
    pt_off = 2200 + 1j * 400
    marker_geometry = []

    poly_1 = []
    poly_1.append(-10 - 10j)
    poly_1.append(-10 + 10j)
    poly_1.append(10 + 10j)
    poly_1.append(10 - 10j)
    marker_geometry.append(poly_1)

    poly_1 = []
    poly_1.append(-100 + 10j)
    poly_1.append(-100 + 100j)
    poly_1.append(-10 + 100j)
    poly_1.append(-10 + 80j)
    poly_1.append(-80 + 80j)
    poly_1.append(-80 + 10j)

    poly_2 = aux_poly.rotate(poly_1, origin=0, degree=90)
    poly_3 = aux_poly.rotate(poly_1, origin=0, degree=180)
    poly_4 = aux_poly.rotate(poly_1, origin=0, degree=270)
    marker_geometry.append(poly_1)
    marker_geometry.append(poly_2)
    marker_geometry.append(poly_3)
    marker_geometry.append(poly_4)

    marker_geometry2 = []
    for poly_1 in marker_geometry:
        poly_1 = np.array(poly_1) + pt_off
        poly_2 = aux_poly.reflect(poly_1, axis='x', value=chip_size[1] / 2)
        poly_3 = aux_poly.reflect(poly_2, axis='y', value=chip_size[0] / 2)
        poly_4 = aux_poly.reflect(poly_3, axis='x', value=chip_size[1] / 2)

        marker_geometry2 += [poly_1, poly_2, poly_3, poly_4]
    marker_geometry = [marker_geometry2]

    # %%
    for num1 in range(layer_count - 1):
        marker_geometry3 = []

        poly_1 = []
        poly_1.append((-10 + 90 * (num1 + 2))
                      + 1j * (-10 + 90 * (num1 + 2)))
        poly_1.append((-10 + 90 * (num1 + 2))
                      + 1j * (10 + 90 * (num1 + 2)))
        poly_1.append((10 + 90 * (num1 + 2))
                      + 1j * (10 + 90 * (num1 + 2)))
        poly_1.append((10 + 90 * (num1 + 2))
                      + 1j * (-10 + 90 * (num1 + 2)))
        poly_1 = np.array(poly_1) + pt_off

        poly_2 = aux_poly.reflect(poly_1, axis='x', value=chip_size[1] / 2)
        poly_3 = aux_poly.reflect(poly_1, axis='y', value=chip_size[0] / 2)
        poly_4 = aux_poly.reflect(poly_2, axis='y', value=chip_size[0] / 2)
        marker_geometry3.append(poly_1)
        marker_geometry3.append(poly_2)
        marker_geometry3.append(poly_3)
        marker_geometry3.append(poly_4)

        marker_geometry.append(marker_geometry3)
        # marker_geometry[0] += marker_geometry3

        marker_geometry4 = []
        ref0 = pt_off + (90 * (num1 + 2) + 30) + 1j * (90 * (num1 + 2) - 90)
        pts = [ref0,
               1j * chip_size[1] + ref0.conjugate(),
               (chip_size[0] + 1j * chip_size[1]) - ref0,
               chip_size[0] - ref0.conjugate()]

        geometry_4 = text(str(num1 + 1), size=1e2)
        for num_2 in range(4):
            marker_geometry4.append(geometry_4[0] + pts[num_2])
        marker_geometry[-1] += marker_geometry4

        print(str(num1 + 1))

    return marker_geometry
