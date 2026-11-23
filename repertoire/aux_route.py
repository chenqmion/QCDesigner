import numpy as np


# %% routing
def route(start, stop, waypoints=(), r=50, straight=0):
    """
    Path between two ports (handshake). The line leaves `start` along start.angle and enters `stop`
    along stop.angle (both angles point outward from their own devices).
    Without waypoints: the shortest path with at most two corners is chosen automatically (straight line,
    one corner at the crossing of the two port axes, or two corners joined by a horizontal / vertical
    section), such that every bend of radius r fits and at least `straight` of straight line is kept
    at each port. When several paths are equally short, the middle section is placed halfway.
    waypoints: points the line passes through, in order. The first/last straight section is extended along
    the port direction until it lines up with the first/last waypoint, so only the middle points are needed.
    Returns the path (list of complex) in the same coordinate frame as start/stop; corners are rounded
    later with radius r by the device that draws it (e.g. cpw_1.new_device).
    """
    u_s = np.exp(1j * start.angle * np.pi / 180)
    u_e = np.exp(1j * stop.angle * np.pi / 180)
    waypoints = [complex(w) for w in waypoints]

    if len(waypoints) == 0:
        path = _auto_path(start.x, u_s, stop.x, u_e, r, straight)
        _check_bend_room(path, r)
        return path

    def lead(port, u, w, name):
        t = (np.conj(u) * (w - port.x)).real
        if t <= 0:
            raise ValueError(f'route: the waypoint {w} is behind port {name}; add a waypoint in front of it.')
        return port.x + t * u

    path = [start.x, lead(start, u_s, waypoints[0], 'start')] + waypoints + \
           [lead(stop, u_e, waypoints[-1], 'stop'), stop.x]
    path = _simplify(path)
    _check_bend_room(path, r)

    return path


def _turn(d0, d1):
    # turning angle (rad, unsigned) from direction d0 to direction d1
    return abs(np.angle(d1 / d0))


def _auto_path(x_s, u_s, x_e, u_e, r, straight, tol=1e-6):
    D = x_e - x_s
    candidates = []  # (length, corners, path)

    # straight line: ports facing each other on the same axis
    if abs(u_s + u_e) < tol and abs((np.conj(u_s) * D).imag) < tol and (np.conj(u_s) * D).real > 0:
        candidates.append((abs(D), 0, [x_s, x_e]))

    # one corner at the crossing of the two port axes
    th = _turn(u_s, -u_e)
    if tol < th < np.pi - tol:
        A = np.array([[u_s.real, -u_e.real], [u_s.imag, -u_e.imag]])
        t1, t2 = np.linalg.solve(A, [D.real, D.imag])
        need = r * np.tan(th / 2) + straight
        if t1 >= need - tol and t2 >= need - tol:
            candidates.append((t1 + t2, 1, [x_s, x_s + t1 * u_s, x_e]))

    # two corners, middle section horizontal or vertical: D + t2*u_e - t1*u_s = m*d with m > 0
    for d in (1, 1j, -1, -1j):
        th1, th2 = _turn(u_s, d), _turn(d, -u_e)
        if th1 > np.pi - tol or th2 > np.pi - tol:
            continue
        T1, T2 = r * np.tan(th1 / 2), r * np.tan(th2 / 2)
        A = np.array([[-u_s.real, u_e.real, -np.real(d)], [-u_s.imag, u_e.imag, -np.imag(d)]])
        if np.linalg.matrix_rank(A, tol=1e-9) < 2:
            continue
        x0 = np.linalg.lstsq(A, [-D.real, -D.imag], rcond=None)[0]   # one solution (t1, t2, m)
        n = np.cross(A[0], A[1])                                       # direction of the solution family
        lo, hi = -np.inf, np.inf
        for xi, ni, ci in zip(x0, n, (T1 + straight, T2 + straight, T1 + T2)):
            if abs(ni) < 1e-12:
                if xi < ci - tol:
                    lo, hi = np.inf, -np.inf
            elif ni > 0:
                lo = max(lo, (ci - xi) / ni)
            else:
                hi = min(hi, (ci - xi) / ni)
        if lo > hi + tol:
            continue
        slope = n.sum()
        if abs(slope) < 1e-9:
            p = (lo + hi) / 2 if np.isfinite(lo) and np.isfinite(hi) else (lo if np.isfinite(lo) else hi)
        else:
            p = lo if slope > 0 else hi
        if not np.isfinite(p):
            continue
        t1, t2, m = x0 + p * n
        p1, p2 = x_s + t1 * u_s, x_e + t2 * u_e
        corners = int(th1 > tol) + int(th2 > tol)
        candidates.append((t1 + t2 + m, corners, [x_s, p1, p2, x_e]))

    if not candidates:
        raise ValueError('route: no path with at most two corners fits between these ports; add waypoints.')
    candidates.sort(key=lambda c: (round(c[0], 6), c[1]))
    return _simplify(candidates[0][2])


def _simplify(path, tol=1e-9):
    # drop repeated points and points lying on a straight line between their neighbours
    pts = [path[0]]
    for p in path[1:]:
        if abs(p - pts[-1]) > tol:
            pts.append(p)
    out = [pts[0]]
    for i in range(1, len(pts) - 1):
        d0 = pts[i] - out[-1]
        d1 = pts[i + 1] - pts[i]
        if abs((np.conj(d0) * d1).imag) > tol * abs(d0) * abs(d1) or (np.conj(d0) * d1).real < 0:
            out.append(pts[i])
    out.append(pts[-1])
    return out


def _check_bend_room(path, r):
    # every corner uses r*tan(theta/2) of each adjacent segment
    tan_len = [0.0]
    for i in range(1, len(path) - 1):
        d0 = path[i] - path[i - 1]
        d1 = path[i + 1] - path[i]
        theta = abs(np.angle(d1 / d0))
        tan_len.append(r * np.tan(theta / 2))
    tan_len.append(0.0)
    for i in range(len(path) - 1):
        need = tan_len[i] + tan_len[i + 1]
        if abs(path[i + 1] - path[i]) < need - 1e-6:
            raise ValueError(f'route: segment {path[i]} -> {path[i + 1]} is shorter than the {need:.1f} '
                             f'needed for bends with r={r}.')
