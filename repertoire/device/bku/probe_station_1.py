import sys

# from spectrum_1 import *

# from shapely.geometry import LinearRing, Polygon, MultiPolygon

sys.path.append('../../geometry')

sys.path.append('../../geometry/device')
from aux_marker import *
from lumped_1 import *


def new_test_pad(width_gap=50, height_gap=50):
    pad = device()

    # %% gap
    poly_1 = []
    if width_gap > 300:
        poly_1.append((-width_gap / 2 - 200, -700 / 2))
        poly_1.append((-width_gap / 2 - 200, 700 / 2))
        poly_1.append((width_gap / 2 + 200, 700 / 2))
        poly_1.append((width_gap / 2 + 200, -700 / 2))
    else:
        poly_1.append((-700 / 2, -700 / 2))
        poly_1.append((-700 / 2, 700 / 2))
        poly_1.append((700 / 2, 700 / 2))
        poly_1.append((700 / 2, -700 / 2))

    poly_2 = []
    poly_2.append((-500 / 2, -500 / 2))
    poly_2.append((-500 / 2, 500 / 2))
    poly_2.append((500 / 2, 500 / 2))
    poly_2.append((500 / 2, -500 / 2))

    poly_1 = ope_hole(poly_1, poly_2)

    poly_3 = []
    if width_gap > 300:
        poly_3.append((-width_gap / 2 - 100, -height_gap / 2 - 100))
        poly_3.append((-width_gap / 2 - 100, height_gap / 2 + 100))
        poly_3.append((-500 / 2, height_gap / 2 + 100))
        poly_3.append((-500 / 2, -height_gap / 2 - 100))

        poly_1 = ope_hole(poly_1, poly_3)
        poly_1 = ope_hole(poly_1, ope_reflect(poly_3[::-1], axis='y', value=0))
        geom_1 = [poly_1]

    else:
        geom_1 = [poly_1]
        if width_gap <= 100:
            poly_3.append((-500 / 2, -100 / 2))
            poly_3.append((-500 / 2, +100 / 2))
            poly_3.append((-300 / 2, +100 / 2))
            poly_3.append((-300 / 2, -100 / 2))
        else:
            poly_3.append((-500 / 2, -100 / 2))
            poly_3.append((-500 / 2, +100 / 2))
            poly_3.append((-width_gap / 2 - 100, +100 / 2))
            poly_3.append((-width_gap / 2 - 100, -100 / 2))

        geom_1.append(poly_3)
        geom_1.append(ope_reflect(poly_3, axis='y', value=0))

    poly_4 = []
    poly_4.append((-100 / 2, -500 / 2))
    poly_4.append((-100 / 2, -height_gap / 2))
    poly_4.append((100 / 2, -height_gap / 2))
    poly_4.append((100 / 2, -500 / 2))

    geom_1.append(poly_4)
    geom_1.append(ope_reflect(poly_4, axis='x', value=0))

    pad.add_geometry('Nb_inv', geom_1)

    # %%
    poly_1 = []
    poly_1.append((-width_gap / 2, -height_gap / 2))
    poly_1.append((-width_gap / 2, height_gap / 2))
    poly_1.append((width_gap / 2, height_gap / 2))
    poly_1.append((width_gap / 2, -height_gap / 2))
    pad.add_geometry('Nb_inv', [poly_1])

    if width_gap > 300:
        pad.add_port(1, (-width_gap / 2 - 200, 0))
        pad.add_port(2, (0, -700 / 2))
        pad.add_port(3, (width_gap / 2 + 200, 0))
        pad.add_port(4, (0, 700 / 2))
    else:
        pad.add_port(1, (-350, 0))
        pad.add_port(2, (0, -700 / 2))
        pad.add_port(3, (350, 0))
        pad.add_port(4, (0, 700 / 2))

    return pad


def new_test_SIS(width_gap=50, height_gap=50,
                 width_nanowire=0.15, length_nanowire=10, width_patch=0.3,
                 over_etch=0.5):
    junction = new_test_pad(width_gap=width_gap, height_gap=height_gap)

    # %% nanowire
    poly_1 = []
    poly_1.append((-width_nanowire / 2, -length_nanowire))
    poly_1.append((-width_nanowire / 2, 0))
    poly_1.append((width_nanowire / 2, 0))
    poly_1.append((width_nanowire / 2, -length_nanowire))

    poly_2 = []
    poly_2.append((-width_nanowire / 2, 0))
    poly_2.append((-width_nanowire / 2, 2 * over_etch))
    poly_2.append((width_nanowire / 2, 2 * over_etch))
    poly_2.append((width_nanowire / 2, 0))

    poly_3 = ope_reflect(poly_2, axis='x', value=-length_nanowire / 2)

    junction.add_geometry('EBL_1', [poly_1, poly_2, poly_3], ref=(0, length_nanowire / np.sqrt(2)), degree=45)
    junction.add_geometry('EBL_1', [poly_1, poly_2, poly_3], ref=(0, length_nanowire / np.sqrt(2)), degree=-45)

    poly_1 = []
    poly_1.append((-width_nanowire / 2, 2 * over_etch))
    poly_1.append((-width_nanowire / 2, 3 * over_etch))
    poly_1.append((width_nanowire / 2, 3 * over_etch))
    poly_1.append((width_nanowire / 2, 2 * over_etch))

    poly_2 = ope_reflect(poly_1, axis='x', value=-length_nanowire / 2)
    junction.add_geometry('EBL_1_ghost', [poly_1, poly_2], ref=(0, length_nanowire / np.sqrt(2)), degree=45)
    junction.add_geometry('EBL_1_ghost', [poly_1, poly_2], ref=(0, length_nanowire / np.sqrt(2)), degree=-45)

    # %% patch
    poly_1 = []
    poly_1.append((-width_gap / 2, -width_patch / 2))
    poly_1.append((-width_gap / 2, width_patch / 2))
    poly_1.append((-length_nanowire / np.sqrt(2), width_patch / 2))
    poly_1.append((-length_nanowire / np.sqrt(2), -width_patch / 2))

    poly_2 = []
    poly_2.append((-width_gap / 2 - 2 * over_etch, -width_patch / 2))
    poly_2.append((-width_gap / 2 - 2 * over_etch, width_patch / 2))
    poly_2.append((-width_gap / 2, width_patch / 2))
    poly_2.append((-width_gap / 2, -width_patch / 2))

    poly_3 = []
    poly_3.append((-length_nanowire / np.sqrt(2), -width_patch / 2))
    poly_3.append((-length_nanowire / np.sqrt(2), width_patch / 2))
    poly_3.append((-length_nanowire / np.sqrt(2) + 2 * over_etch, width_patch / 2))
    poly_3.append((-length_nanowire / np.sqrt(2) + 2 * over_etch, -width_patch / 2))

    junction.add_geometry('EBL_1', [poly_1, poly_2, poly_3])
    junction.add_geometry('EBL_1', [poly_1, poly_2, poly_3], degree=180)

    poly_1 = []
    poly_1.append((-width_gap / 2 - 3 * over_etch, -width_patch / 2))
    poly_1.append((-width_gap / 2 - 3 * over_etch, width_patch / 2))
    poly_1.append((-width_gap / 2 - 2 * over_etch, width_patch / 2))
    poly_1.append((-width_gap / 2 - 2 * over_etch, -width_patch / 2))

    poly_2 = []
    poly_2.append((-length_nanowire / np.sqrt(2) + 2 * over_etch, -width_patch / 2))
    poly_2.append((-length_nanowire / np.sqrt(2) + 2 * over_etch, width_patch / 2))
    poly_2.append((-length_nanowire / np.sqrt(2) + 3 * over_etch, width_patch / 2))
    poly_2.append((-length_nanowire / np.sqrt(2) + 3 * over_etch, -width_patch / 2))

    junction.add_geometry('EBL_1_ghost', [poly_1, poly_2])
    junction.add_geometry('EBL_1_ghost', [poly_1, poly_2], degree=180)

    return junction


def new_test_SISQUID(width_gap=50, height_gap=50,
                     width_nanowire=0.15, length_nanowire=10,
                     width_patch=0.3, gap_patch=5,
                     over_etch=0.5):
    junction = new_test_pad(width_gap=width_gap, height_gap=height_gap)

    # %% nanowire
    JJ = device()

    poly_1 = []
    poly_1.append((-width_nanowire / 2, -length_nanowire))
    poly_1.append((-width_nanowire / 2, 0))
    poly_1.append((width_nanowire / 2, 0))
    poly_1.append((width_nanowire / 2, -length_nanowire))

    poly_2 = []
    poly_2.append((-width_nanowire / 2, 0))
    poly_2.append((-width_nanowire / 2, 2 * over_etch))
    poly_2.append((width_nanowire / 2, 2 * over_etch))
    poly_2.append((width_nanowire / 2, 0))

    poly_3 = ope_reflect(poly_2, axis='x', value=-length_nanowire / 2)

    JJ.add_geometry('EBL_1', [poly_1, poly_2, poly_3], ref=(0, length_nanowire / np.sqrt(2)), degree=45)
    JJ.add_geometry('EBL_1', [poly_1, poly_2, poly_3], ref=(0, length_nanowire / np.sqrt(2)), degree=-45)

    # junction.add_geometry('EBL_1', [poly_1, poly_2, poly_3], ref=(0, -length_nanowire / np.sqrt(2)), degree=135)
    # junction.add_geometry('EBL_1', [poly_1, poly_2, poly_3], ref=(0, -length_nanowire / np.sqrt(2)), degree=-135)

    poly_1 = []
    poly_1.append((-width_nanowire / 2, 2 * over_etch))
    poly_1.append((-width_nanowire / 2, 3 * over_etch))
    poly_1.append((width_nanowire / 2, 3 * over_etch))
    poly_1.append((width_nanowire / 2, 2 * over_etch))

    poly_2 = ope_reflect(poly_1, axis='x', value=-length_nanowire / 2)
    JJ.add_geometry('EBL_1_ghost', [poly_1, poly_2], ref=(0, length_nanowire / np.sqrt(2)), degree=45)
    JJ.add_geometry('EBL_1_ghost', [poly_1, poly_2], ref=(0, length_nanowire / np.sqrt(2)), degree=-45)

    # %% patch
    poly_1 = []
    poly_1.append((-width_gap / 2, -width_patch / 2))
    poly_1.append((-width_gap / 2, width_patch / 2))
    poly_1.append((-length_nanowire / np.sqrt(2), width_patch / 2))
    poly_1.append((-length_nanowire / np.sqrt(2), -width_patch / 2))

    poly_2 = []
    poly_2.append((-width_gap / 2 - 2 * over_etch, -width_patch / 2))
    poly_2.append((-width_gap / 2 - 2 * over_etch, width_patch / 2))
    poly_2.append((-width_gap / 2, width_patch / 2))
    poly_2.append((-width_gap / 2, -width_patch / 2))

    poly_3 = []
    poly_3.append((-length_nanowire / np.sqrt(2), -width_patch / 2))
    poly_3.append((-length_nanowire / np.sqrt(2), width_patch / 2))
    poly_3.append((-length_nanowire / np.sqrt(2) + 2 * over_etch, width_patch / 2))
    poly_3.append((-length_nanowire / np.sqrt(2) + 2 * over_etch, -width_patch / 2))

    JJ.add_geometry('EBL_1', [poly_1, poly_2, poly_3])
    JJ.add_geometry('EBL_1', [poly_1, poly_2, poly_3], degree=180)

    poly_1 = []
    poly_1.append((-width_gap / 2 - 3 * over_etch, -width_patch / 2))
    poly_1.append((-width_gap / 2 - 3 * over_etch, width_patch / 2))
    poly_1.append((-width_gap / 2 - 2 * over_etch, width_patch / 2))
    poly_1.append((-width_gap / 2 - 2 * over_etch, -width_patch / 2))

    poly_2 = []
    poly_2.append((-length_nanowire / np.sqrt(2) + 2 * over_etch, -width_patch / 2))
    poly_2.append((-length_nanowire / np.sqrt(2) + 2 * over_etch, width_patch / 2))
    poly_2.append((-length_nanowire / np.sqrt(2) + 3 * over_etch, width_patch / 2))
    poly_2.append((-length_nanowire / np.sqrt(2) + 3 * over_etch, -width_patch / 2))

    JJ.add_geometry('EBL_1_ghost', [poly_1, poly_2])
    JJ.add_geometry('EBL_1_ghost', [poly_1, poly_2], degree=180)

    junction.combine_device(JJ, ref=(0, gap_patch / 2))
    junction.combine_device(JJ, ref=(0, -gap_patch / 2), axis='x')

    return junction


def new_test_SISQUID2(width_gap=50, height_gap=50,
                      width_nanowire=0.15, length_nanowire=10,
                      width_patch=0.3, gap_patch=5,
                      over_etch=0.5):
    junction = new_test_pad(width_gap=width_gap, height_gap=height_gap)

    # %% nanowire
    length_nanowire_1 = length_nanowire - gap_patch / 2
    length_nanowire_2 = length_nanowire + gap_patch / 2
    length_nanowire_list = [length_nanowire_1, length_nanowire_2]
    JJ = device()
    for num in range(2):
        length_nanowire = length_nanowire_list[num]

        poly_1 = []
        poly_1.append((-width_nanowire / 2, -length_nanowire))
        poly_1.append((-width_nanowire / 2, 0))
        poly_1.append((width_nanowire / 2, 0))
        poly_1.append((width_nanowire / 2, -length_nanowire))

        poly_2 = []
        poly_2.append((-width_nanowire / 2, 0))
        poly_2.append((-width_nanowire / 2, 2 * over_etch))
        poly_2.append((width_nanowire / 2, 2 * over_etch))
        poly_2.append((width_nanowire / 2, 0))

        poly_3 = ope_reflect(poly_2, axis='x', value=-length_nanowire / 2)

        if num == 0:
            JJ.add_geometry('EBL_1', [poly_1, poly_2, poly_3], ref=(0, length_nanowire / np.sqrt(2)), degree=45)
            JJ.add_geometry('EBL_1', [poly_1, poly_2, poly_3], ref=(0, length_nanowire / np.sqrt(2)), degree=-45)
        else:
            JJ.add_geometry('EBL_1', [poly_1, poly_2, poly_3], ref=(0, -length_nanowire / np.sqrt(2)), degree=135)
            JJ.add_geometry('EBL_1', [poly_1, poly_2, poly_3], ref=(0, -length_nanowire / np.sqrt(2)), degree=-135)

        poly_1 = []
        poly_1.append((-width_nanowire / 2, 2 * over_etch))
        poly_1.append((-width_nanowire / 2, 3 * over_etch))
        poly_1.append((width_nanowire / 2, 3 * over_etch))
        poly_1.append((width_nanowire / 2, 2 * over_etch))

        poly_2 = ope_reflect(poly_1, axis='x', value=-length_nanowire / 2)
        if num == 0:
            JJ.add_geometry('EBL_1_ghost', [poly_1, poly_2], ref=(0, length_nanowire / np.sqrt(2)), degree=45)
            JJ.add_geometry('EBL_1_ghost', [poly_1, poly_2], ref=(0, length_nanowire / np.sqrt(2)), degree=-45)
        else:
            JJ.add_geometry('EBL_1_ghost', [poly_1, poly_2], ref=(0, -length_nanowire / np.sqrt(2)), degree=135)
            JJ.add_geometry('EBL_1_ghost', [poly_1, poly_2], ref=(0, -length_nanowire / np.sqrt(2)), degree=-135)

    # %% patch
    length_nanowire = length_nanowire_1

    poly_1 = []
    poly_1.append((-width_gap / 2, -width_patch / 2))
    poly_1.append((-width_gap / 2, width_patch / 2))
    poly_1.append((-length_nanowire / np.sqrt(2), width_patch / 2))
    poly_1.append((-length_nanowire / np.sqrt(2), -width_patch / 2))

    poly_2 = []
    poly_2.append((-width_gap / 2 - 2 * over_etch, -width_patch / 2))
    poly_2.append((-width_gap / 2 - 2 * over_etch, width_patch / 2))
    poly_2.append((-width_gap / 2, width_patch / 2))
    poly_2.append((-width_gap / 2, -width_patch / 2))

    poly_3 = []
    poly_3.append((-length_nanowire / np.sqrt(2), -width_patch / 2))
    poly_3.append((-length_nanowire / np.sqrt(2), width_patch / 2))
    poly_3.append((-length_nanowire / np.sqrt(2) + 2 * over_etch, width_patch / 2))
    poly_3.append((-length_nanowire / np.sqrt(2) + 2 * over_etch, -width_patch / 2))

    JJ.add_geometry('EBL_1', [poly_1, poly_2, poly_3])
    JJ.add_geometry('EBL_1', [poly_1, poly_2, poly_3], degree=180)

    poly_1 = []
    poly_1.append((-width_gap / 2 - 3 * over_etch, -width_patch / 2))
    poly_1.append((-width_gap / 2 - 3 * over_etch, width_patch / 2))
    poly_1.append((-width_gap / 2 - 2 * over_etch, width_patch / 2))
    poly_1.append((-width_gap / 2 - 2 * over_etch, -width_patch / 2))

    poly_2 = []
    poly_2.append((-length_nanowire / np.sqrt(2) + 2 * over_etch, -width_patch / 2))
    poly_2.append((-length_nanowire / np.sqrt(2) + 2 * over_etch, width_patch / 2))
    poly_2.append((-length_nanowire / np.sqrt(2) + 3 * over_etch, width_patch / 2))
    poly_2.append((-length_nanowire / np.sqrt(2) + 3 * over_etch, -width_patch / 2))

    JJ.add_geometry('EBL_1_ghost', [poly_1, poly_2])
    JJ.add_geometry('EBL_1_ghost', [poly_1, poly_2], degree=180)

    junction.combine_device(JJ, ref=(0, gap_patch / 2))
    # junction.combine_device(JJ, ref=(0, -gap_patch / 2), axis='x')

    return junction


def new_test_SNS(width_gap=100, height_gap=50,
                 width_nanowire=0.15, length_nanowire=10, width_patch=0.3,
                 over_etch=0.5):
    # width_gap = length_nanowire - 2

    junction = new_test_pad(width_gap=width_gap, height_gap=height_gap)

    # %% nanowire
    poly_1 = []
    poly_1.append((-length_nanowire / 2, -width_nanowire / 2))
    poly_1.append((-length_nanowire / 2, width_nanowire / 2))
    poly_1.append((length_nanowire / 2, width_nanowire / 2))
    poly_1.append((length_nanowire / 2, -width_nanowire / 2))

    poly_2 = []
    poly_2.append((-length_nanowire / 2 - 2 * over_etch, -width_nanowire / 2))
    poly_2.append((-length_nanowire / 2 - 2 * over_etch, width_nanowire / 2))
    poly_2.append((-length_nanowire / 2, width_nanowire / 2))
    poly_2.append((-length_nanowire / 2, -width_nanowire / 2))

    poly_3 = ope_reflect(poly_2, axis='y', value=0)

    junction.add_geometry('EBL_1', [poly_1, poly_2, poly_3])
    junction.add_geometry('EBL_1', [poly_1, poly_2, poly_3])

    poly_1 = []
    poly_1.append((-length_nanowire / 2 - 3 * over_etch, -width_nanowire / 2))
    poly_1.append((-length_nanowire / 2 - 3 * over_etch, width_nanowire / 2))
    poly_1.append((-length_nanowire / 2 - 2 * over_etch, width_nanowire / 2))
    poly_1.append((-length_nanowire / 2 - 2 * over_etch, -width_nanowire / 2))

    poly_2 = ope_reflect(poly_1, axis='y', value=0)
    junction.add_geometry('EBL_1_ghost', [poly_1, poly_2])
    junction.add_geometry('EBL_1_ghost', [poly_1, poly_2])

    # %% patch
    poly_1 = []
    poly_1.append((-length_nanowire / 2 - width_patch / 2, -height_gap / 2))
    poly_1.append((-length_nanowire / 2 - width_patch / 2, 0))
    poly_1.append((-length_nanowire / 2 + width_patch / 2, 0))
    poly_1.append((-length_nanowire / 2 + width_patch / 2, -height_gap / 2))

    poly_2 = []
    poly_2.append((-length_nanowire / 2 - width_patch / 2, -height_gap / 2 - 2 * over_etch))
    poly_2.append((-length_nanowire / 2 - width_patch / 2, -height_gap / 2))
    poly_2.append((-length_nanowire / 2 + width_patch / 2, -height_gap / 2))
    poly_2.append((-length_nanowire / 2 + width_patch / 2, -height_gap / 2 - 2 * over_etch))

    poly_3 = []
    poly_3.append((-length_nanowire / 2 - width_patch / 2, 0))
    poly_3.append((-length_nanowire / 2 - width_patch / 2, 2 * over_etch))
    poly_3.append((-length_nanowire / 2 + width_patch / 2, 2 * over_etch))
    poly_3.append((-length_nanowire / 2 + width_patch / 2, 0))

    junction.add_geometry('EBL_1', [poly_1, poly_2, poly_3])
    junction.add_geometry('EBL_1', [poly_1, poly_2, poly_3], degree=180)

    poly_1 = []
    poly_1.append((-length_nanowire / 2 - width_patch / 2, -height_gap / 2 - 3 * over_etch))
    poly_1.append((-length_nanowire / 2 - width_patch / 2, -height_gap / 2 - 2 * over_etch))
    poly_1.append((-length_nanowire / 2 + width_patch / 2, -height_gap / 2 - 2 * over_etch))
    poly_1.append((-length_nanowire / 2 + width_patch / 2, -height_gap / 2 - 3 * over_etch))

    poly_2 = []
    poly_2.append((-length_nanowire / 2 - width_patch / 2, 2 * over_etch))
    poly_2.append((-length_nanowire / 2 - width_patch / 2, 3 * over_etch))
    poly_2.append((-length_nanowire / 2 + width_patch / 2, 3 * over_etch))
    poly_2.append((-length_nanowire / 2 + width_patch / 2, 2 * over_etch))

    junction.add_geometry('EBL_1_ghost', [poly_1, poly_2])
    junction.add_geometry('EBL_1_ghost', [poly_1, poly_2], degree=180)

    return junction


def new_test_SNSs(width_gap=100, height_gap=50,
                  width_nanowire=0.15, length_nanowire=10, width_patch=0.3,
                  over_etch=0.5,
                  width_island=0.3, height_island=1, gap_island=0.3, num_island=3):
    junction = new_test_SNS(width_gap=width_gap, height_gap=height_gap,
                            width_nanowire=width_nanowire, length_nanowire=length_nanowire, width_patch=width_patch,
                            over_etch=over_etch)

    # %% islands
    width_1 = num_island * width_island + (num_island - 1) * gap_island

    for num_1 in range(num_island):
        x_1 = (-width_1 / 2 + width_island / 2) + num_1 * (width_island + gap_island)

        poly_1 = []
        poly_1.append((x_1 - width_island / 2, -height_island / 2))
        poly_1.append((x_1 - width_island / 2, height_island / 2))
        poly_1.append((x_1 + width_island / 2, height_island / 2))
        poly_1.append((x_1 + width_island / 2, -height_island / 2))

        poly_2 = []
        poly_2.append((x_1 - width_island / 2, -height_island / 2 - 2 * over_etch))
        poly_2.append((x_1 - width_island / 2, -height_island / 2))
        poly_2.append((x_1 + width_island / 2, -height_island / 2))
        poly_2.append((x_1 + width_island / 2, -height_island / 2 - 2 * over_etch))

        poly_3 = ope_reflect(poly_2, axis='x', value=0)

        junction.add_geometry('EBL_1', [poly_1, poly_2, poly_3])

        poly_1 = []
        poly_1.append((x_1 - width_island / 2, -height_island / 2 - 3 * over_etch))
        poly_1.append((x_1 - width_island / 2, -height_island / 2 - 2 * over_etch))
        poly_1.append((x_1 + width_island / 2, -height_island / 2 - 2 * over_etch))
        poly_1.append((x_1 + width_island / 2, -height_island / 2 - 3 * over_etch))

        poly_2 = ope_reflect(poly_1, axis='x', value=0)

        junction.add_geometry('EBL_1_ghost', [poly_1, poly_2])

    return junction
