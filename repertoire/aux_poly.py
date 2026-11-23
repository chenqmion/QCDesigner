import numpy as np
import klayout.db as db


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
    dbu = 1e-3

    def to_region(poly):
        pts = [db.Point(round(np.real(z) * 1/dbu), round(np.imag(z) * 1/dbu))
               for z in poly]
        return db.Region(db.Polygon(pts))

    area_3 = to_region(poly_1) - to_region(poly_2)

    geometry_3 = []
    for p in area_3.each():
        p.resolve_holes()
        pts = np.array([(pt.x * dbu, pt.y * dbu) for pt in p.each_point_hull()])
        geometry_3.append(pts[:, 0] + 1j * pts[:, 1])

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
