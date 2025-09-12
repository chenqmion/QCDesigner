import sys

sys.path.append('../')

from lumped_1 import *


def new_bolometer(nanowire={'a': 0.2, 'l_1': 1, 'l_2': 0.3, 'l_3': 0.5, 'da_shadow': 0.0, 'l_shadow': 0.5},
                  line_in={'a': 0.3, 'l': 5, 'da_shadow': 0.0, 'l_shadow': 0.5},
                  line_gnd={'a': 0.3, 'l': 5, 'da_shadow': 0.0, 'l_shadow': 0.5},
                  line_array={'a': 0.3, 'l': 2.5, 'da_shadow': 0.0, 'l_shadow': 0.5, 'N': 6},
                  line_out={'a': 0.3, 'l': 5, 'da_shadow': 0.0, 'l_shadow': 0.5},
                  layer=['AuPd', 'Al', 'Nb_inv']):
    bolometer_1 = device()

    junction_1 = bolometer_junction(nanowire=nanowire, line_in=line_in, line_gnd=line_gnd, line_array=line_array,
                                    line_out=line_out, layer=layer)
    new_ports = bolometer_1.combine_device(junction_1, ref=(0, 0), degree=0, port=1)

    thermometer_1 = lumped_resonator(s=3, w=50, h=100, N_list=[6, 6], spine={'a': 10, 'ref_y': 0}, gap=10,
                                     layer='Nb_inv')

    new_ports = bolometer_1.combine_device(thermometer_1, ref=new_ports['2'], degree=0, axis='y', port=2)

    # %% ports
    bolometer_1.add_port(1, (0, 0))
    bolometer_1.add_port(2, new_ports['2'])

    return bolometer_1


def bolometer_junction(nanowire={'a': 0.2, 'l_1': 1, 'l_2': 0.3, 'l_3': 0.5, 'da_shadow': 0.0, 'l_shadow': 0.5},
                       line_in={'a': 0.3, 'l': 5, 'da_shadow': 0.0, 'l_shadow': 0.5},
                       line_gnd={'a': 0.3, 'l': 5, 'da_shadow': 0.0, 'l_shadow': 0.5},
                       line_array={'a': 0.3, 'l': 2.5, 'da_shadow': 0.0, 'l_shadow': 0.5, 'N': 6},
                       line_out={'a': 0.3, 'l': 5, 'da_shadow': 0.0, 'l_shadow': 0.5},
                       layer=['AuPd', 'Al', 'Nb_inv']):
    junction_1 = device()

    cross_1 = new_cross(
        length_list=[nanowire['l_3'] + line_in['a'] / 2, line_array['l'] / 2, (nanowire['l_1'] + line_in['a']) / 2,
                     line_in['l']], a_list=[nanowire['a'], line_in['a']], layer=layer,
        shadow={'da_list': [nanowire['da_shadow'], line_in['da_shadow']],
                'length_list': [nanowire['l_shadow'], line_in['l_shadow'], 0, line_in['l_shadow']]})
    new_ports = junction_1.combine_device(cross_1, ref=(0, 0), degree=0, port=1)

    cross_2 = new_cross(
        length_list=[(nanowire['l_1'] + line_gnd['a']) / 2, line_gnd['l'], (nanowire['l_2'] + line_gnd['a']) / 2,
                     line_array['l'] / 2], a_list=[nanowire['a'], line_gnd['a']], layer=layer,
        shadow={'da_list': [nanowire['da_shadow'], line_gnd['da_shadow']],
                'length_list': [0, line_gnd['l_shadow'], 0, line_gnd['l_shadow']]})
    new_ports = junction_1.combine_device(cross_2, ref=new_ports['3'], degree=0, port=1)

    cross_3 = new_cross(length_list=[(nanowire['l_2'] + line_array['a']) / 2, line_array['l'] / 2,
                                     (nanowire['l_2'] + line_array['a']) / 2, line_array['l'] / 2],
                        a_list=[nanowire['a'], line_array['a']], layer=layer,
                        shadow={'da_list': [nanowire['da_shadow'], line_array['da_shadow']],
                                'length_list': [0, line_array['l_shadow'], 0, line_array['l_shadow']]})
    for num1 in range(line_array['N']):
        new_ports = junction_1.combine_device(cross_3, ref=new_ports['3'], degree=0, port=1)

    cross_4 = new_cross(
        length_list=[(nanowire['l_2'] + line_out['a']) / 2, line_array['l'] / 2, nanowire['l_3'] + line_out['a'] / 2,
                     line_out['l']], a_list=[nanowire['a'], line_out['a']], layer=layer,
        shadow={'da_list': [nanowire['da_shadow'], line_out['da_shadow']],
                'length_list': [0, line_out['l_shadow'], nanowire['l_shadow'], line_out['l_shadow']]})
    new_ports = junction_1.combine_device(cross_4, ref=new_ports['3'], degree=0, port=1)

    # %% ports
    junction_1.add_port(1, (0, 0))
    junction_1.add_port(2, new_ports['3'])

    return junction_1
