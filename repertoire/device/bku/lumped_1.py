import sys

sys.path.append('../')
from geometry_class import *


# %% capacitor
def capacitor_fishbone(input={'a': 10, 'b': 6, 'l': 0, 'ref_y': 0},
                       output={'a': 10, 'b': 6, 'l': 0, 'ref_y': 0},
                       spine={'a': 10, 'ref_y': 0},
                       s=3, w=50, h=100, N=1, layer='Nb_inv'):
    capacitor = device()

    N2 = 2 * N - 1
    h2 = (h - s - spine['a']) / 2

    if input['l'] < 0:
        ref2 = s
    else:
        ref2 = input['l'] + s

    teeth = capacitor_teeth(s=s, w=w, h=h2 + spine['ref_y'], N=N2, layer=layer)
    new_ports = capacitor.combine_device(teeth, ref=(ref2, -(h + s + spine['a'] - 2 * spine['ref_y']) / 4), degree=0,
                                         port=1)

    teeth2 = capacitor_teeth(s=s, w=w, h=h2 - spine['ref_y'], N=N2, layer=layer)
    new_ports = capacitor.combine_device(teeth2, ref=(ref2, (h + s + spine['a'] + 2 * spine['ref_y']) / 4), degree=0,
                                         axis='x', port=1)

    # %% input
    geometry_1 = []

    if input['l'] < 0:
        poly_1 = []
        poly_1.append([0, -(h + s) / 2])
        poly_1.append([0, (h + s) / 2])
        poly_1.append([s, (h + s) / 2])
        poly_1.append([s, -(h + s) / 2])
        geometry_1.append(poly_1)

    else:
        poly_1 = []
        poly_1.append([0, input['ref_y'] + input['a'] / 2])
        poly_1.append([0, input['ref_y'] + input['a'] / 2 + input['b']])
        poly_1.append([input['l'], input['ref_y'] + input['a'] / 2 + input['b']])
        poly_1.append([input['l'], (h + s) / 2])
        poly_1.append([input['l'] + s, (h + s) / 2])
        poly_1.append([input['l'] + s, input['ref_y'] + input['a'] / 2])
        geometry_1.append(poly_1)

        poly_2 = []
        poly_2.append([0, input['ref_y'] - input['a'] / 2 - input['b']])
        poly_2.append([0, input['ref_y'] - input['a'] / 2])
        poly_2.append([input['l'] + s, input['ref_y'] - input['a'] / 2])
        poly_2.append([input['l'] + s, -(h + s) / 2])
        poly_2.append([input['l'], -(h + s) / 2])
        poly_2.append([input['l'], input['ref_y'] - input['a'] / 2 - input['b']])
        geometry_1.append(poly_2)

    # %% output
    if output['l'] < 0:
        poly_1 = []
        poly_1.append([0, -(h + s) / 2])
        poly_1.append([0, (h + s) / 2])
        poly_1.append([s, (h + s) / 2])
        poly_1.append([s, -(h + s) / 2])
        geometry_1.append(np.add((new_ports['3'][0], 0), poly_1))
    else:
        poly_1 = []
        poly_1.append([0, output['ref_y'] + output['a'] / 2])
        poly_1.append([0, (h + s) / 2])
        poly_1.append([s, (h + s) / 2])
        poly_1.append([s, output['ref_y'] + output['a'] / 2 + output['b']])
        poly_1.append([output['l'] + s, output['ref_y'] + output['a'] / 2 + output['b']])
        poly_1.append([output['l'] + s, output['ref_y'] + output['a'] / 2])
        geometry_1.append(np.add((new_ports['3'][0], 0), poly_1))

        poly_2 = []
        poly_2.append([0, -(h + s) / 2])
        poly_2.append([0, output['ref_y'] - output['a'] / 2])
        poly_2.append([output['l'] + s, output['ref_y'] - output['a'] / 2])
        poly_2.append([output['l'] + s, output['ref_y'] - output['a'] / 2 - output['b']])
        poly_2.append([s, output['ref_y'] - output['a'] / 2 - output['b']])
        poly_2.append([s, -(h + s) / 2])
        geometry_1.append(np.add((new_ports['3'][0], 0), poly_2))

    capacitor.add_geometry(layer=layer, geometry=geometry_1)

    # %% ports
    capacitor.add_port(1, (0, input['ref_y']))
    if output['l'] < 0:
        capacitor.add_port(2, (new_ports['3'][0] + s, output['ref_y']))
    else:
        capacitor.add_port(2, (new_ports['3'][0] + output['l'] + s, output['ref_y']))

    return capacitor


# def capacitor_fishbone(s=3, w=50, h=100, N=1, spine = {'a':10, 'ref_y':0}, layer='Nb_inv'):
#     capacitor = device()
#
#     h2 = (h-s-spine['a'])/2
#     teeth = capacitor_teeth(s=s, w=w, h=h2+spine['ref_y'], N=N, layer=layer)
#     new_ports = capacitor.combine_device(teeth, ref=(s, -(h+s+spine['a']-2*spine['ref_y'])/4), degree=0, port=1)
#
#     teeth2 = capacitor_teeth(s=s, w=w, h=h2 - spine['ref_y'], N=N, layer=layer)
#     new_ports = capacitor.combine_device(teeth2, ref=(s, (h + s + spine['a']+2*spine['ref_y'])/4), degree=0, axis='x', port=1)
#
#     # %% ports
#     capacitor.add_port(1, (0, 0))
#     capacitor.terminate_port(1, width=2*(h2+s)+spine['a'], gap=s, degree=0, layer=layer)
#
#     capacitor.add_port(2, (new_ports['3'][0],spine['ref_y']))
#
#     return capacitor

def capacitor_taper(s=3, w=50, h=100, N=2, layer='Nb_inv',
                    a_list=[10, 0, 10], b_list=[6, 10, 6], length_list=[50, 200, 50]):
    capacitor = device()

    # %% taper_1
    a2 = N * w - s

    taper_1 = new_taper(length=length_list[0], a=a_list[0], b=b_list[0], a2=a2, b2=b_list[1])
    new_ports = capacitor.combine_device(taper_1, ref=(0, 0), degree=0, port=1)

    cpw = new_cpw(path=[(0, 0), (length_list[1] / 2, 0)], a=a2, b=b_list[1])
    new_ports = capacitor.combine_device(cpw, ref=new_ports['2'], degree=0, port=1)

    teeth = capacitor_teeth(s=s, w=w, h=h, N=N, layer=layer)
    new_ports = capacitor.combine_device(teeth, ref=np.subtract(new_ports['2'], ((h + s) / 2, 0)), degree=90, port=4)

    new_ports = capacitor.combine_device(cpw, ref=np.subtract(new_ports['2'], ((h + s) / 2, 0)), degree=0, port=1)

    taper_2 = new_taper(length=length_list[2], a=a2, b=b_list[1], a2=a_list[2], b2=b_list[2])
    new_ports = capacitor.combine_device(taper_2, ref=new_ports['2'], degree=0, port=1)

    # %% ports
    capacitor.add_port(1, (0, 0))
    capacitor.add_port(2, new_ports['2'])

    return capacitor


def capacitor_teeth(s=3, w=50, h=100, N=1, gap=10, layer='Nb_inv'):
    capacitor = device()

    poly_1 = []
    poly_1.append([w - s, -s / 2])
    poly_1.append([0, -s / 2])
    poly_1.append([0, s / 2])
    poly_1.append([w - s, s / 2])

    poly_1.append([w - s, h + s / 2])
    poly_1.append([w, h + s / 2])
    poly_1.append([w, -s / 2])

    poly_2 = []
    poly_2.append([w - s, h - s / 2])
    poly_2.append([0, h - s / 2])
    poly_2.append([0, h + s / 2])
    poly_2.append([w - s, h + s / 2])

    poly_2.append([w, h + s / 2])
    poly_2.append([w, - s / 2])
    poly_2.append([w - s, - s / 2])

    geometry_1 = []
    for num1 in range(N):
        if num1 != N - 1:
            if num1 % 2 == 0:
                geometry_1.append(np.add(poly_1, (num1 * w, -h / 2)))
            else:
                geometry_1.append(np.add(poly_2, (num1 * w, -h / 2)))
        else:
            if num1 % 2 == 0:
                geometry_1.append(np.add(poly_1[:4], (num1 * w, -h / 2)))
            else:
                geometry_1.append(np.add(poly_2[:4], (num1 * w, -h / 2)))

    # %% gap
    x_total = N * w - s
    capacitor.add_geometry(layer=layer, geometry=geometry_1)

    # %% ports
    capacitor.add_port(1, (0, 0))
    capacitor.add_port(2, (x_total / 2, -(h + s) / 2))
    capacitor.add_port(3, (x_total, 0))
    capacitor.add_port(4, (x_total / 2, (h + s) / 2))

    return capacitor


# %%
def inductor_meander(input={'a': 3, 'l': 10, 'ref_y': 0}, output={'a': 3, 'l': 10, 'ref_y': 0},
                     s=3, w=50, h=100, N=1, gap=3, layer='Nb_inv'):
    meander = device()

    indoctor = inductor_teeth(s=s, w=w, h=h, N=N, gap=gap, layer=layer)
    new_ports = meander.combine_device(indoctor, ref=(input['l'] + s, 0), degree=0, port=1)

    # %% input
    geometry_1 = []

    poly_1 = []
    poly_1.append([0, -(h + s) / 2 - gap])
    poly_1.append([0, input['ref_y'] - input['a'] / 2])
    poly_1.append([input['l'], input['ref_y'] - input['a'] / 2])
    poly_1.append([input['l'], -(h + s) / 2])
    poly_1.append([input['l'] + s, -(h + s) / 2])
    poly_1.append([input['l'] + s, -(h + s) / 2 - gap])
    geometry_1.append(poly_1)

    poly_2 = []
    poly_2.append([0, input['ref_y'] + input['a'] / 2])
    poly_2.append([0, (h + s) / 2 + gap])
    poly_2.append([input['l'] + s, (h + s) / 2 + gap])
    poly_2.append([input['l'] + s, input['ref_y'] + input['a'] / 2])
    geometry_1.append(poly_2)

    # %% output
    ref_y = (-1) ** (N % 2) * output['ref_y']

    poly_1 = []
    poly_1.append([0, (h + s) / 2])
    poly_1.append([0, (h + s) / 2 + gap])
    poly_1.append([output['l'] + s, (h + s) / 2 + gap])
    poly_1.append([output['l'] + s, ref_y + output['a'] / 2])
    poly_1.append([s, ref_y + output['a'] / 2])
    poly_1.append([s, (h + s) / 2])

    poly_2 = []
    poly_2.append([0, -(h + s) / 2 - gap])
    poly_2.append([0, ref_y - output['a'] / 2])
    poly_2.append([output['l'] + s, ref_y - output['a'] / 2])
    poly_2.append([output['l'] + s, -(h + s) / 2 - gap])

    if N % 2 == 1:
        poly_1 = ope_reflect(poly_1, axis='x', value=0)
        poly_2 = ope_reflect(poly_2, axis='x', value=0)

    geometry_1.append(np.add(new_ports['2'], poly_1))
    geometry_1.append(np.add(new_ports['2'], poly_2))

    meander.add_geometry(layer=layer, geometry=geometry_1)

    # %% ports
    meander.add_port(1, (0, input['ref_y']))
    meander.add_port(2, (new_ports['2'][0] + output['l'] + s, ref_y))

    return meander


def inductor_teeth(s=3, w=50, h=100, N=1, gap=3, layer='Nb_inv'):
    inductor = device()

    poly_1 = []
    poly_1.append([0, s / 2])
    poly_1.append([0, h + s / 2])
    poly_1.append([w - s, h + s / 2])
    poly_1.append([w - s, s / 2])

    poly_2 = []
    poly_2.append([0, -s / 2])
    poly_2.append([0, h - s / 2])
    poly_2.append([w - s, h - s / 2])
    poly_2.append([w - s, -s / 2])

    geometry_1 = []
    for num1 in range(N):
        if num1 % 2 == 0:
            geometry_1.append(np.add(poly_1, (num1 * w, -h / 2)))
        else:
            geometry_1.append(np.add(poly_2, (num1 * w, -h / 2)))

    # %% gap
    x_total = N * w - s

    poly_1 = []
    poly_1.append((-x_total / 2, 0))
    poly_1.append((-x_total / 2, gap))
    poly_1.append((x_total / 2, gap))
    poly_1.append((x_total / 2, 0))

    poly_2 = ope_reflect(poly_1, axis='x', value=0)

    geometry_1.append(np.add(poly_1, (x_total / 2, (h + s) / 2)))
    geometry_1.append(np.add(poly_2, (x_total / 2, -(h + s) / 2)))

    inductor.add_geometry(layer=layer, geometry=geometry_1)

    # %% ports
    inductor.add_port(1, (0, 0))
    inductor.add_port(2, (x_total, 0))

    return inductor


# %% resonator
def lumped_resonator(spine={'a': 10, 'ref_y': 0},
                     tip_y=0,
                     N_list=[1, 1], gap=10,
                     s=3, w=50, h=100, layer='Nb_inv'):
    resonator = device()
    taper_length = (spine['a'] - s) / 2

    capacitor = capacitor_fishbone(input={'a': spine['a'], 'b': s, 'l': -1, 'ref_y': 0},
                                   output={'a': spine['a'], 'b': s, 'l': w - s - taper_length, 'ref_y': spine['ref_y']},
                                   spine=spine,
                                   s=s, w=w, h=h, N=N_list[0], layer=layer)
    new_ports = resonator.combine_device(capacitor, ref=(0, 0), degree=0, port=1)

    taper = new_taper(length=taper_length, a=spine['a'], b=s, a2=s, b2=(spine['a'] + s) / 2)
    new_ports = resonator.combine_device(taper, ref=new_ports['2'], degree=0, port=1)

    indoctor = inductor_meander(input={'a': s, 'l': w - s, 'ref_y': spine['ref_y']},
                                output={'a': s, 'l': w - s, 'ref_y': tip_y},
                                s=s, w=w, h=h, N=N_list[1], gap=gap, layer=layer)
    new_ports = resonator.combine_device(indoctor, ref=new_ports['2'], degree=0, port=1)

    # %% ports
    resonator.add_port(1, (0, 0))
    resonator.add_port(2, new_ports['2'])

    return resonator
