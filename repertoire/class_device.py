from dataclasses import dataclass, field

import numpy as np

import aux_poly
import aux_route


# %%
@dataclass()
class handshake():
    x: complex = None
    angle: float = None


def _normalize_angle(angle):
    return float(np.round(np.mod(angle, 360), 9)) % 360


def _reflect_angle(angle, axis):
    # reflection about a horizontal line (axis='x') flips the y component; axis='y' flips the x component
    if axis == 'x':
        return -angle
    elif axis == 'y':
        return 180 - angle
    return angle


@dataclass()
class device():
    ports: dict[handshake] = field(default_factory=lambda: {})
    layers: dict[str] = field(default_factory=lambda: {})
    routes: list = field(default_factory=lambda: [])

    def combine_device(self, device, ref=None, degree=0, axis=None, port=None, target=None):
        """
        Two usages:
        1) Manual: ref + degree (old behaviour).
        2) Handshake: port + target. `target` is a handshake on the existing side; `port` is the name of
           the port of `device` to be connected. The rotation is computed automatically so that the two
           angles are opposite; `ref` and `degree` are ignored. For a gap or an extra rotation, pass a
           manually constructed handshake as `target`.
        """
        device.route_all()  # draw pending routes of the device before copying its geometry

        if port is None:
            ref_port = 0
            deg_port = 0
        else:
            ref_port = device.ports[port].x
            deg_port = device.ports[port].angle

        if target is not None:
            if port is None:
                raise ValueError('combine_device: `port` must be given when `target` is used.')
            if target.angle is None or deg_port is None:
                raise ValueError('combine_device: both ports need an angle for handshake.')
            # angle of the device port after the optional reflection
            deg_port_reflected = _reflect_angle(deg_port, axis)
            # after rotation: deg_port_reflected + degree == target.angle + 180
            degree = _normalize_angle(target.angle + 180 - deg_port_reflected)
            ref = target.x

        if ref is None:
            d_vector = 0 + 0j
        else:
            if type(ref) == handshake:
                d_vector = ref.x - ref_port
            else:
                d_vector = ref - ref_port

        for num_layer, key_layer in enumerate(list(device.layers.keys())):
            val_geometry = (device.layers[key_layer]).copy()
            self.add_geometry(layer=key_layer, geometry=val_geometry, ref=d_vector, degree=degree, axis=axis,
                              ref_port=ref_port)

        # ports
        new_ports = {}
        if len(device.ports) != 0:
            for num_port, key_port in enumerate(list(device.ports.keys())):
                if axis == 'x':
                    val_port = aux_poly.reflect([device.ports[key_port].x], axis='x', value=np.imag(ref_port))
                elif axis == 'y':
                    val_port = aux_poly.reflect([device.ports[key_port].x], axis='y', value=np.real(ref_port))
                else:
                    val_port = device.ports[key_port].x

                _port = aux_poly.rotate(val_port, origin=ref_port, degree=degree).item()
                _angle = device.ports[key_port].angle
                if _angle is not None:
                    _angle = _normalize_angle(_reflect_angle(_angle, axis) + degree)
                new_ports[key_port] = handshake(x=_port + d_vector, angle=_angle)

        return new_ports

    def route(self, start, stop, waypoints=(), a=10, b=6, r=50, straight=0, clearance=20,
              terminate=None, fix=False, d_rad=np.pi / 36, layer='Nb_inv'):
        """
        Register a CPW between two ports (handshake). Nothing is drawn yet: all registered CPWs are routed
        and drawn by route_all(), which is called automatically by chip.gen_gds() and when this device is
        combined into another one. At that moment every component already in this device is an obstacle;
        the CPW (total width a + 2b) keeps at least `clearance` from them and from the other CPWs.
        All pending CPWs are routed together: each takes its shortest candidate path, and only CPWs that
        would come too close to each other are moved to other candidates (aux_route.choose).
        Path rules: see aux_route.route.
        terminate: None, or keyword arguments for terminate_port() to give the stop end an open end,
        e.g. dict(width=22, gap=6).
        fix: if True, the CPW follows [start, *waypoints, stop] exactly and is never changed. Fixed CPWs are
        drawn first; they must keep `clearance` from the components and from each other (otherwise an error
        is raised), and all other CPWs avoid them.
        """
        self.routes.append(dict(start=start, stop=stop, waypoints=tuple(waypoints), a=a, b=b, r=r,
                                straight=straight, clearance=clearance, terminate=terminate, fix=fix,
                                d_rad=d_rad, layer=layer, device=None))

    def route_all(self):
        """Route and draw all registered CPWs that are not drawn yet: fixed ones first, then the others."""
        pending = [(n, req) for n, req in enumerate(self.routes) if req['device'] is None]
        if not pending:
            return

        def label(n, req):
            return f"route #{n} ({req['start'].x} -> {req['stop'].x})"

        def width(req):
            return req['a'] + 2 * req['b']

        # 1) fixed CPWs: taken as given, checked against the components and each other, drawn first
        fixed = [(n, req) for n, req in pending if req['fix']]
        obstacles = aux_route.obstacle_region(self)
        fixed_paths, fixed_bands = [], []
        for n, req in fixed:
            try:
                path = aux_route.fixed_path(req['start'], req['stop'], req['waypoints'], r=req['r'])
            except ValueError as e:
                raise ValueError(f'{label(n, req)}: {e}') from None
            loc = aux_route._hit(path, req['r'], width(req), req['clearance'], obstacles)
            if loc is not None:
                raise ValueError(f'{label(n, req)}: the fixed path comes closer than {req["clearance"]} to a '
                                 f'component near {loc}.')
            fixed_paths.append(path)
            fixed_bands.append(aux_route.band(path, req['r'], width(req)))
        for i in range(len(fixed)):
            for j in range(i + 1, len(fixed)):
                cl = max(fixed[i][1]['clearance'], fixed[j][1]['clearance'])
                if aux_route.too_close(fixed_bands[i], fixed_bands[j], cl):
                    raise ValueError(f'{label(*fixed[i])} and {label(*fixed[j])}: the fixed paths come closer '
                                     f'than {cl}.')
        for (n, req), path in zip(fixed, fixed_paths):
            self._draw_route(req, path)

        # 2) the other CPWs: routed together, avoiding everything drawn so far (incl. the fixed CPWs)
        free = [(n, req) for n, req in pending if not req['fix']]
        if not free:
            return
        obstacles = aux_route.obstacle_region(self)
        candidate_lists = []
        for n, req in free:
            try:
                candidate_lists.append(aux_route.paths(req['start'], req['stop'], req['waypoints'],
                                                       r=req['r'], straight=req['straight']))
            except ValueError as e:
                raise ValueError(f'{label(n, req)}: {e}') from None

        def allowed(i, k):  # obstacle check, done only for the candidates that are actually considered
            req = free[i][1]
            return aux_route._hit(candidate_lists[i][k], req['r'], width(req), req['clearance'], obstacles) is None

        try:
            choice = aux_route.choose(candidate_lists,
                                      widths=[width(req) for _, req in free],
                                      rs=[req['r'] for _, req in free],
                                      clearances=[req['clearance'] for _, req in free],
                                      labels=[label(n, req) for n, req in free],
                                      allowed=allowed)
        except ValueError as e:
            # give the precise message for a blocked line with waypoints
            for i, (n, req) in enumerate(free):
                if req['waypoints'] and str(e).startswith(label(n, req)):
                    msg = aux_route.blocked_message(req['start'], req['stop'], req['waypoints'],
                                                    candidate_lists[i], req['r'], width(req),
                                                    req['clearance'], obstacles)
                    raise ValueError(f'{label(n, req)}: {msg}') from None
            raise
        for (n, req), paths, k in zip(free, candidate_lists, choice):
            self._draw_route(req, paths[k])

    def _draw_route(self, req, path):
        import cpw_1  # the CPW drawing lives in device/cpw_1.py
        cpw = cpw_1.new_device(path, a=req['a'], b=req['b'], r=req['r'], d_rad=req['d_rad'], layer=req['layer'])
        if req['terminate'] is not None:
            cpw.terminate_port('2', **req['terminate'])
        self.combine_device(cpw)
        req['device'] = cpw

    def add_geometry(self, layer, geometry, ref=(0 + 0j), degree=0, axis=None, ref_port=0):
        geometry2 = []
        for num_poly, val_poly in enumerate(geometry):
            if axis == 'x':
                val_poly = aux_poly.reflect(val_poly, axis='x', value=np.imag(ref_port))
            elif axis == 'y':
                val_poly = aux_poly.reflect(val_poly, axis='y', value=np.real(ref_port))

            val_poly = aux_poly.rotate(val_poly, origin=ref_port, degree=degree)
            val_poly = list(val_poly + ref)
            geometry2.append(val_poly)

        if layer in list(self.layers.keys()):
            self.layers[layer] += geometry2
        else:
            self.layers[layer] = geometry2

    def add_port(self, name, ref_port, degree=0):
        self.ports[name] = handshake(x=ref_port, angle=degree)

    def terminate_port(self, name_port, width=22, gap=6, degree=0, layer='Nb_inv'):
        poly_1 = [-1j * width / 2]
        poly_1.append(1j * width / 2)
        poly_1.append(gap + 1j * width / 2)
        poly_1.append(gap - 1j * width / 2)

        ref_port = self.ports[name_port].x
        deg_port = self.ports[name_port].angle
        self.add_geometry(layer, [poly_1], ref=ref_port, degree=deg_port)
