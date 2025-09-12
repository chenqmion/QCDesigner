import gdsfactory as gf

import numpy as np


# %%
def rotate(poly, origin=(0 + 0j), degree=0):
    poly_new = origin + (np.array(poly) - origin) * np.exp(1j * degree * np.pi / 180)
    return np.ravel(poly_new)


def reflect(poly, axis='x', value=0):
    if axis == 'x':
        poly_new = np.real(poly) + 1j * (2 * value - np.imag(poly))
    else:
        poly_new = (2 * value - np.real(poly)) + 1j * np.imag(poly)
    return np.ravel(poly_new)


def subtract(poly_1, poly_2):
    device_1 = gf.Component()
    _poly_1 = device_1.add_polygon(np.array([np.real(poly_1), np.imag(poly_1)]).T, layer=(0, 0))
    area_1 = gf.Region(_poly_1.polygon)

    _poly_2 = device_1.add_polygon(np.array([np.real(poly_2), np.imag(poly_2)]).T, layer=(0, 0))
    area_2 = gf.Region(_poly_2.polygon)

    device_2 = gf.Component()
    area_3 = area_1 - area_2
    device_2.add_polygon(area_3, layer=(0, 0))
    _poly_3 = device_2.get_polygons_points()

    geometry_3 = []
    for num_poly, val_poly in enumerate(list(_poly_3.values())[0]):
        geometry_3.append(val_poly[:, 0] + 1j * val_poly[:, 1])

    return geometry_3

# def merge(poly_1, poly_2):
#     device_1 = gf.Component()
#     _poly_1 = device_1.add_polygon(np.array([np.real(poly_1), np.imag(poly_1)]).T, layer=(0, 0))
#     area_1 = gf.Region(_poly_1.polygon)
#
#     _poly_2 = device_1.add_polygon(np.array([np.real(poly_2), np.imag(poly_2)]).T, layer=(0, 0))
#     area_2 = gf.Region(_poly_2.polygon)
#
#     device_2 = gf.Component()
#     area_3 = area_1 + area_2
#     device_2.add_polygon(area_3, layer=(0, 0))
#     _poly_3 = device_2.get_polygons_points()
#
#     poly_3 = np.squeeze(list(_poly_3.values()))
#
#     return poly_3[:,0] + 1j*poly_3[:,1]

#
# poly_1 = []
# poly_1.append(-1 - 1j)
# poly_1.append(-1 + 1j)
# poly_1.append(1 + 1j)
# poly_1.append(1 - 1j)
#
# poly_2 = []
# poly_2.append(-1 / 2 - 1j / 2)
# poly_2.append(-1 / 2 + 1j / 2)
# poly_2.append(1 / 2 + 1j / 2)
# poly_2.append(1 / 2 - 1j / 2)
#
# poly_3 = subtract(poly_1, poly_2)
