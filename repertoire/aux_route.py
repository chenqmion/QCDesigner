import klayout.db as db
import numpy as np

DBU = 1e-3  # database unit used for the obstacle check (um)


# %% routing
def route(start, stop, waypoints=(), r=50, straight=0, obstacles=None, width=0, clearance=0):
    """
    Path between two ports (handshake). The line leaves `start` along start.angle and enters `stop`
    along stop.angle (both angles point outward from their own devices).
    Without waypoints: candidate paths with at most two corners are generated (straight line, one corner at
    the crossing of the two port axes, or two corners joined by a horizontal / vertical section), such that
    every bend of radius r fits and at least `straight` of straight line is kept at each port. The shortest
    candidate that does not hit an obstacle is returned; among equally short ones the middle section is
    placed halfway.
    waypoints: points the line passes through, in order. The first/last straight section is extended along
    the port direction until it lines up with the first/last waypoint, so only the middle points are needed.
    obstacles: device, klayout Region, or a list of them. The line (rounded corners, total width `width`)
    must stay at least `clearance` away from them; the part within width / 2 + clearance of the two ports is
    not checked, since the line is supposed to touch the devices it connects.
    Returns the path (list of complex) in the same coordinate frame as start/stop; corners are rounded
    later with radius r by the device that draws it (e.g. cpw_1.new_device).
    """
    obs = obstacle_region(obstacles)
    all_paths = paths(start, stop, waypoints, r, straight)
    for path in all_paths:  # shortest first; stop at the first one that is free
        if obs is None or _hit(path, r, width, clearance, obs) is None:
            return path
    raise ValueError(blocked_message(start, stop, waypoints, all_paths, r, width, clearance, obs))


def candidates(start, stop, waypoints=(), r=50, straight=0, obstacles=None, width=0, clearance=0):
    """All paths allowed by the rules of route() that do not hit an obstacle, shortest first."""
    obs = obstacle_region(obstacles)
    all_paths = paths(start, stop, waypoints, r, straight)
    free = [p for p in all_paths if obs is None or _hit(p, r, width, clearance, obs) is None]
    if not free:
        raise ValueError(blocked_message(start, stop, waypoints, all_paths, r, width, clearance, obs))
    return free


def blocked_message(start, stop, waypoints, all_paths, r, width, clearance, obs):
    """Error text when every path hits an obstacle."""
    if len(waypoints) > 0:
        loc = _hit(all_paths[0], r, width, clearance, obs)
        return f'route: the path through the given waypoints hits an obstacle near {loc}.'
    return f'route: all {len(all_paths)} candidate paths between {start.x} and {stop.x} hit an obstacle; ' \
           f'add waypoints.'


def paths(start, stop, waypoints=(), r=50, straight=0):
    """Candidate paths by the rules of route(), shortest first, without looking at obstacles."""
    u_s = np.exp(1j * start.angle * np.pi / 180)
    u_e = np.exp(1j * stop.angle * np.pi / 180)
    waypoints = [complex(w) for w in waypoints]

    if len(waypoints) == 0:
        found = _auto_candidates(start.x, u_s, stop.x, u_e, r, straight)
        if not found:
            raise ValueError('route: no path with at most two corners fits between these ports; add waypoints.')
        return found

    def lead(port, u, w, name):
        t = (np.conj(u) * (w - port.x)).real
        if t <= 0:
            raise ValueError(f'route: the waypoint {w} is behind port {name}; add a waypoint in front of it.')
        return port.x + t * u

    path = [start.x, lead(start, u_s, waypoints[0], 'start')] + waypoints + \
           [lead(stop, u_e, waypoints[-1], 'stop'), stop.x]
    path = _simplify(path)
    _check_bend_room(path, r)
    return [path]


def fixed_path(start, stop, waypoints=(), r=50):
    """
    Path [start.x, *waypoints, stop.x] taken as given (no points added). The first section must leave start
    along start.angle, the last one must enter stop along stop.angle, and every bend of radius r must fit.
    """
    path = _simplify([complex(start.x)] + [complex(w) for w in waypoints] + [complex(stop.x)])
    if len(path) < 2:
        raise ValueError('route: start and stop coincide.')
    for port, d, name in ((start, path[1] - path[0], 'start'), (stop, path[-2] - path[-1], 'stop')):
        u = np.exp(1j * port.angle * np.pi / 180)
        if abs(np.angle(d / u)) > 1e-6:
            raise ValueError(f'route: the fixed path does not leave port {name} at {port.x} along its angle '
                             f'{port.angle}; first/last waypoint must lie on the port axis.')
    _check_bend_room(path, r)
    return path


def band(path, r, width):
    """Region covered by a line of total width `width` along the path with corners rounded by r."""
    pts = [db.DPoint(z.real, z.imag) for z in centerline(path, r)]
    return db.Region(db.DPath(pts, width).polygon().to_itype(DBU))


def too_close(band_1, band_2, clearance):
    """True if the two regions come closer than clearance."""
    gap = int(round(clearance / DBU))
    return band_1.bbox().enlarged(gap, gap).overlaps(band_2.bbox()) and \
        not (band_1.sized(gap) & band_2).is_empty()


# %% several lines without overlap
def choose(candidate_lists, widths, rs, clearances, labels=None, allowed=None, max_nodes=100000):
    """
    Pick one path per line from its candidates (shortest first) such that no two lines come closer than
    their clearance (the larger of the two), with the smallest total length.
    allowed(i, k): optional test whether candidate k of line i may be used at all (e.g. obstacle check);
    it is only called for candidates that are actually considered.
    The shortest allowed candidate of every line is tried first; only lines that conflict are changed.
    Returns the list of chosen indices. Raises ValueError naming the conflicting lines if impossible.
    """
    n = len(candidate_lists)
    labels = labels or [f'#{i}' for i in range(n)]
    lengths = [[sum(abs(np.diff(p))) for p in c] for c in candidate_lists]
    bands, cache, ok = {}, {}, {}

    def usable(i, k):
        if allowed is None:
            return True
        if (i, k) not in ok:
            ok[(i, k)] = allowed(i, k)
        return ok[(i, k)]

    first = []
    for i in range(n):
        k0 = next((k for k in range(len(candidate_lists[i])) if usable(i, k)), None)
        if k0 is None:
            raise ValueError(f'{labels[i]}: all {len(candidate_lists[i])} candidate paths hit an obstacle; '
                             f'add waypoints.')
        first.append(k0)

    def line(i, k):
        if (i, k) not in bands:
            bands[(i, k)] = band(candidate_lists[i][k], rs[i], widths[i])
        return bands[(i, k)]

    def conflict(i, k, j, l):
        key = (i, k, j, l) if i < j else (j, l, i, k)
        if key not in cache:
            cache[key] = too_close(line(i, k), line(j, l), max(clearances[i], clearances[j]))
        return cache[key]

    # lines in conflict with the all-shortest choice are searched first
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n) if conflict(i, first[i], j, first[j])]
    if not pairs:
        return first
    involved = {i for p in pairs for i in p}
    order = sorted(range(n), key=lambda i: (i not in involved, i))
    rest = [sum(lengths[order[q]][first[order[q]]] for q in range(pos, n)) for pos in range(n + 1)]

    best = {'total': np.inf, 'choice': None}
    nodes = [0]
    chosen = {}

    def search(pos, total):
        if total + rest[pos] >= best['total'] - 1e-9 or nodes[0] > max_nodes:
            return
        if pos == n:
            best['total'], best['choice'] = total, [chosen[i] for i in range(n)]
            return
        i = order[pos]
        for k in range(first[i], len(candidate_lists[i])):
            nodes[0] += 1
            if not usable(i, k) or any(conflict(i, k, j, l) for j, l in chosen.items()):
                continue
            chosen[i] = k
            search(pos + 1, total + lengths[i][k])
            del chosen[i]

    search(0, 0.0)
    if best['choice'] is None:
        names = ', '.join(f'{labels[i]} / {labels[j]}' for i, j in pairs)
        raise ValueError(f'route: no combination of candidate paths keeps these lines apart: {names}; '
                         f'add waypoints.')
    return best['choice']


# %% obstacles
def obstacle_region(obstacles, skip_layers=('remarks',)):
    """
    Merge obstacles into one klayout Region (in DBU). Accepts None, a klayout Region, a device
    (all layers except skip_layers), or a list of these.
    """
    if obstacles is None:
        return None
    if isinstance(obstacles, db.Region):
        return obstacles
    if isinstance(obstacles, (list, tuple)):
        region = db.Region()
        for o in obstacles:
            region += obstacle_region(o, skip_layers)
        return region.merged()
    region = db.Region()
    for key, polys in obstacles.layers.items():
        if key in skip_layers:
            continue
        for poly in polys:
            pts = np.atleast_1d(np.squeeze(np.asarray(poly, dtype=complex)))
            if len(pts) >= 3:
                region.insert(db.DPolygon([db.DPoint(z.real, z.imag) for z in pts]).to_itype(DBU))
    return region.merged()


def centerline(path, r, d_rad=np.pi / 36):
    """Centre line of the path with every corner rounded by radius r (list of complex)."""
    out = [path[0]]
    for i in range(1, len(path) - 1):
        d0 = (path[i] - path[i - 1]) / abs(path[i] - path[i - 1])
        d1 = (path[i + 1] - path[i]) / abs(path[i + 1] - path[i])
        th = np.angle(d1 / d0)
        tl = r * np.tan(abs(th) / 2)
        p_in = path[i] - tl * d0
        center = p_in + r * d0 * 1j * np.sign(th)
        n = max(2, int(np.ceil(abs(th) / d_rad)) + 1)
        out += list(center + (p_in - center) * np.exp(1j * np.linspace(0, th, n)))
    out.append(path[-1])
    return out


def _hit(path, r, width, clearance, obs):
    """None if the line keeps `clearance` from obs, otherwise the approximate location of the first hit."""
    pts = [db.DPoint(z.real, z.imag) for z in centerline(path, r)]
    band = db.Region(db.DPath(pts, width + 2 * clearance).polygon().to_itype(DBU))
    m = width / 2 + clearance
    for z in (path[0], path[-1]):
        box = db.DBox(z.real - m, z.imag - m, z.real + m, z.imag + m)
        band -= db.Region(db.DPolygon.ellipse(box, 64).to_itype(DBU))
    hit = band & (obs & db.Region(band.bbox()))  # only the obstacles near the line
    if hit.is_empty():
        return None
    # report the hit closest to the start of the line
    centers = [p.bbox().center() for p in hit.each()]
    z0 = path[0] / DBU
    c = min(centers, key=lambda c: abs(complex(c.x, c.y) - z0))
    return complex(round(c.x * DBU, 1), round(c.y * DBU, 1))


def _turn(d0, d1):
    # turning angle (rad, unsigned) from direction d0 to direction d1
    return abs(np.angle(d1 / d0))


def _auto_candidates(x_s, u_s, x_e, u_e, r, straight, n_shift=9, tol=1e-6):
    """All candidate paths with at most two corners, shortest first."""
    D = x_e - x_s
    candidates = []  # (length, corners, distance from the preferred position, path)

    # straight line: ports facing each other on the same axis
    if abs(u_s + u_e) < tol and abs((np.conj(u_s) * D).imag) < tol and (np.conj(u_s) * D).real > 0:
        candidates.append((abs(D), 0, 0, [x_s, x_e]))

    # one corner at the crossing of the two port axes
    th = _turn(u_s, -u_e)
    if tol < th < np.pi - tol:
        A = np.array([[u_s.real, -u_e.real], [u_s.imag, -u_e.imag]])
        t1, t2 = np.linalg.solve(A, [D.real, D.imag])
        need = r * np.tan(th / 2) + straight
        if t1 >= need - tol and t2 >= need - tol:
            candidates.append((t1 + t2, 1, 0, [x_s, x_s + t1 * u_s, x_e]))

    # two corners, middle section horizontal or vertical: D + t2*u_e - t1*u_s = m*d with m > 0
    # the solutions form a one-parameter family (the middle section slides); besides the preferred
    # position, n_shift shifted positions are kept as alternatives for avoiding obstacles
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
            p0 = (lo + hi) / 2 if np.isfinite(lo) and np.isfinite(hi) else (lo if np.isfinite(lo) else hi)
        else:
            p0 = lo if slope > 0 else hi
        if not np.isfinite(p0):
            continue
        if np.isfinite(lo) and np.isfinite(hi):
            shifts = np.linspace(lo, hi, n_shift)
        else:
            step = abs(D) / 4 / np.linalg.norm(n)
            sign = 1 if np.isfinite(lo) else -1
            shifts = p0 + sign * step * np.arange(1, n_shift)
        corners = int(th1 > tol) + int(th2 > tol)
        scale = np.linalg.norm(n)
        for p in [p0] + list(shifts):
            t1, t2, m = x0 + p * n
            path = [x_s, x_s + t1 * u_s, x_e + t2 * u_e, x_e]
            candidates.append((t1 + t2 + m, corners, abs(p - p0) * scale, path))

    candidates.sort(key=lambda c: (round(c[0], 6), c[1], round(c[2], 6)))
    out = []
    for c in candidates:
        path = _simplify(c[3])
        if not any(len(path) == len(q) and np.allclose(path, q) for q in out):
            out.append(path)
    return out


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
