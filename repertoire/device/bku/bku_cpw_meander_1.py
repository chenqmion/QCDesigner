import sys

import numpy as np

sys.path.append('../')


def cpw_inline(pt_start=0, pt_stop=None,
               length=1000, width=None, N=0,
               a=10, b=6, r=50, d_rad=np.pi / 36):
    if N == 0:
        pre = length / 2
        post = length / 2

        if pt_stop == None:
            ph_x = 0
        else:
            dx = pt_stop - pt_start
            ph_x = np.angle(dx)

    else:
        if width == None:
            if pt_stop == None:
                ph_x = 0

                pre = r
                post = r
            else:
                dx = pt_stop - pt_start
                ph_x = np.angle(dx)
                dx2 = np.abs(dx)

                pre = (dx2 - 2 * r * N) / 2
                post = (dx2 - 2 * r * N) / 2

            width = ((length - (pre + post - 2 * r) - (N + 1) * np.pi * r) + 2 * (N + 1) * r) / N
        else:
            ph_x = 0
            pre = (length - (N + 1) * np.pi * r - (N * width - 2 * (N + 1) * r)) / 2 + r
            post = (length - (N + 1) * np.pi * r - (N * width - 2 * (N + 1) * r)) / 2 + r

    # %%
    path = [0, pre]

    pt_x = pre
    for num_1 in range(N):
        if num_1 % 2 == 0:
            path.append(pt_x
                        + 1j * (width / 2))
            path.append((pt_x + 2 * r)
                        + 1j * (width / 2))
            path.append(pt_x + 2 * r)
        else:
            path.append(pt_x
                        - 1j * (width / 2))
            path.append((pt_x + 2 * r)
                        - 1j * (width / 2))
            path.append(pt_x + 2 * r)
        pt_x += 2 * r

    path.append(pt_x + post)
    path = np.array(path) * np.exp(1j * ph_x) + pt_start
    cpw = cpw_1.new_cpw(path, a=a, b=b, r=r)

    cpw.add_port(1, path[0])
    cpw.add_port(2, path[-1])

    return cpw


def cpw_offline(pt_start=0,
                length=1850, width=200, N=4,
                a=10, b=6, r=50, d_rad=np.pi / 36,
                mode='compact'):
    pre = r
    if width == None:
        post = r
        width = (length - N * np.pi * r) / (N - 1) + 2 * r

    else:
        # overwrite N
        N = int(np.ceil((length - np.pi * r) / (width - 2 * r + np.pi * r)))
        post = length - (N - 1) * (width - 2 * r) - N * np.pi * r

    # %%
    path = [0]

    pt_y = 0
    for num_1 in range(N):
        if num_1 % 2 == 0:
            path.append(pre + 1j * pt_y)
            path.append(pre + 1j * (pt_y - 2 * r))
        else:
            path.append(-(width - pre) + 1j * pt_y)
            path.append(-(width - pre) + 1j * (pt_y - 2 * r))
        pt_y += -2 * r

    if mode == 'compact':
        if (post <= (width - 2 * r)):
            if N % 2 == 0:
                path.append(path[-1] + r + post)
            else:
                path.append(path[-1] - r - post)
        else:
            phase_post = (post - (width - 2 * r)) / r
            if N % 2 == 0:
                path.append(path[-1] + width - r)
                ori_post = path[-1] - 1j * r
                phase_post = -phase_post
            else:
                path.append(path[-1] - width + r)
                ori_post = path[-1] - 1j * r

        path = np.array(path) + pt_start
        cpw = cpw_1.new_cpw(path, a=a, b=b, r=r)

        cpw.add_port(1, path[0])

        if (post > (width - 2 * r)):
            cpw_post = cpw_1.cpw_curve(path[-1], ori_post + pt_start, phase_post, a=a, b=b, d_rad=d_rad)
            cpw.add_geometry('Nb_inv', cpw_post)

            cpw.add_port(2, (ori_post + pt_start) + (path[-1] - (ori_post + pt_start)) * np.exp(1j * phase_post))
        else:
            cpw.add_port(2, path[-1])

    else:
        path.append(path[-1] - 1j * (post + np.pi * r / 2))
        path = np.array(path) + pt_start
        cpw = cpw_1.new_cpw(path, a=a, b=b, r=r)

        cpw.add_port(1, path[0])
        cpw.add_port(2, path[-1])

    return cpw

# design = geo.design(name='cpw_meander', time='250602', logo='QCD')
# cpw = cpw_inline()
# design.add_device(cpw)
#
# cpw2 = cpw_offline(pt_start=-1000j, width=200, mode='compact')
# design.add_device(cpw2)
#
# design.gen_gds()
