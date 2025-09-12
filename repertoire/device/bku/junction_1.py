import sys

sys.path.append('../')
import geometry_class as geo


def new_cross(length_list=[100, 100, 100, 100], a_list=[10, 10], layer=['AuPd', 'Al'],
              shadow={'da_list': [0, 0], 'length_list': [0.5, 0.5, 0.5, 0.5]}):
    cross = geo.device()

    poly_1 = [shadow['length_list'][0] - 1j * a_list[0] / 2]
    poly_1.append(shadow['length_list'][0] + 1j * a_list[0] / 2)
    poly_1.append(-shadow['length_list'][2] + length_list[0] + length_list[2] + 1j * a_list[0] / 2)
    poly_1.append(-shadow['length_list'][2] + length_list[0] + length_list[2] - 1j * a_list[0] / 2)
    cross.add_geometry(layer=layer[0], geometry=[poly_1])

    poly_2 = [(length_list[0] - a_list[1] / 2) + 1j * (-length_list[1] + shadow['length_list'][1])]
    poly_2.append((length_list[0] - a_list[1] / 2) + 1j * (length_list[3] - shadow['length_list'][3]))
    poly_2.append((length_list[0] + a_list[1] / 2) + 1j * (length_list[3] - shadow['length_list'][3]))
    poly_2.append((length_list[0] + a_list[1] / 2) + 1j * (-length_list[1] + shadow['length_list'][1]))
    cross.add_geometry(layer=layer[1], geometry=[poly_2])

    # poly_3 = [(0, -length_list[1])]
    # poly_3.append((0, length_list[3]))
    # poly_3.append((length_list[0] + length_list[2], length_list[3]))
    # poly_3.append((length_list[0] + length_list[2], -length_list[1]))
    # cross.add_geometry(layer=layer[2], geometry=[poly_3])

    cross.add_port(1, length_list[0] + length_list[2])
    cross.add_port(2, length_list[0] + 1j * length_list[3])
    cross.add_port(3, 0)
    cross.add_port(4, length_list[0] - 1j * length_list[1])

    # %% shadow
    for num_shadow, shadow_length in enumerate(shadow['length_list']):
        if shadow_length != 0:
            shadow_layer = layer[num_shadow % 2] + '_shadow'
            cross.terminate_port(num_shadow + 1, width=a_list[num_shadow % 2] + shadow['da_list'][num_shadow % 2],
                                 gap=shadow['length_list'][num_shadow],
                                 degree=num_shadow * 90, layer=shadow_layer)

    return cross


def new_junction(N=1, length_list=[100, 100, 100, 100], a_list=[10, 10], width=2, y_shift=0,
                 layer=['AuPd', 'Al', 'Nb_inv']):
    junction = geo.device()

    cross_1 = new_cross(length_list=length_list, a_list=a_list, layer=layer)
    # cross_1.terminate_port(2, width=(length_list[0]+length_list[2]), gap=width/2-length_list[1] + y_shift, degree=270, layer=layer[2])
    # cross_1.terminate_port(4, width=(length_list[0]+length_list[2]), gap=width/2-length_list[3] - y_shift, degree=90, layer=layer[2])

    new_ports = junction.combine_device(cross_1, ref=0, degree=0, port=1)
    for num1 in range(N - 1):
        new_ports = junction.combine_device(cross_1, ref=new_ports['3'], degree=0, port=1)

    junction.add_port(1, 0)
    junction.add_port(2, new_ports['3'])

    return junction

# def new_cross(length_list=[100, 100, 100, 100], a_list=[10, 10, 10, 10], layer=['AuPd', 'Al', 'Nb_inv']):
#     cross = device()
#
#     poly_1 = [(0, -a_list[0] / 2)]
#     poly_1.append((0, a_list[0] / 2))
#     poly_1.append((length_list[0] - a_list[3] / 2, a_list[0] / 2))
#     poly_1.append((length_list[0] - a_list[3] / 2, length_list[3]))
#     poly_1.append((length_list[0] + a_list[3] / 2, length_list[3]))
#     poly_1.append((length_list[0] + a_list[3] / 2, a_list[2] / 2))
#     poly_1.append((length_list[0] + length_list[2], a_list[2] / 2))
#     poly_1.append((length_list[0] + length_list[2], -a_list[2] / 2))
#     poly_1.append((length_list[0] + a_list[1] / 2, -a_list[2] / 2))
#     poly_1.append((length_list[0] + a_list[1] / 2, -length_list[1]))
#     poly_1.append((length_list[0] - a_list[1] / 2, -length_list[1]))
#     poly_1.append((length_list[0] - a_list[1] / 2, -a_list[0] / 2))
#     cross.add_geometry(layer=layer[0], geometry=[poly_1])
#
#     poly_2 = [(0, -length_list[1])]
#     poly_2.append((0, length_list[3]))
#     poly_2.append((length_list[0] + length_list[2], length_list[3]))
#     poly_2.append((length_list[0] + length_list[2], -length_list[1]))
#     cross.add_geometry(layer=layer[2], geometry=[poly_2])
#
#     cross.add_port(1, (0, 0))
#     cross.add_port(2, (length_list[0], -length_list[1]))
#     cross.add_port(3, (length_list[0] + length_list[2], 0))
#     cross.add_port(4, (length_list[0], length_list[3]))
#
#     return cross

# patch_geometry = []
#
# poly_12 = [(0, -length_list[1])]
# poly_12.append((0, -a_list[0]/2))
# poly_12.append((length_list[0] - a_list[1]/2, -a_list[0]/2))
# poly_12.append((length_list[0] - a_list[1]/2, -length_list[1]))
# patch_geometry.append(poly_12)
#
# poly_14 = [(0, a_list[0]/2)]
# poly_14.append((0, length_list[3]))
# poly_14.append((length_list[0]-a_list[3]/2, length_list[3]))
# poly_14.append((length_list[0]-a_list[3]/2, a_list[0]/2))
# patch_geometry.append(poly_14)
#
# poly_32 = [(length_list[0] + a_list[1] / 2, -length_list[1])]
# poly_32.append((length_list[0] + a_list[1] / 2, -a_list[2]/2))
# poly_32.append((length_list[0]+length_list[2], -a_list[2]/2))
# poly_32.append((length_list[0]+length_list[2], -length_list[1]))
# patch_geometry.append(poly_32)
#
# poly_34 = [(length_list[0] + a_list[3] / 2, a_list[2] / 2)]
# poly_34.append((length_list[0] + a_list[3] / 2, length_list[3]))
# poly_34.append((length_list[0]+length_list[2], length_list[3]))
# poly_34.append((length_list[0]+length_list[2], a_list[2] / 2))
# patch_geometry.append(poly_34)
#
# cross.add_geometry('Nb_inv', patch_geometry)
