from dataclasses import dataclass, field
import numpy as np
import aux_poly

# %%
@dataclass()
class handshake():
    x: complex = None
    angle: float = None

@dataclass()
class device():
    ports: dict[handshake] = field(default_factory=lambda: {})
    layers: dict[str] = field(default_factory=lambda: {})

    def combine_device(self, device, ref=None, degree=0, axis=None, port=None):
        if port == None:
            ref_port = 0
            deg_port = 0
        else:
            ref_port = device.ports[port].x
            deg_port = device.ports[port].angle

        if ref == None:
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
                    val_port = [device.ports[key_port].x]

                _port = aux_poly.rotate(val_port, origin=ref_port, degree=degree)
                new_ports[key_port] = handshake(x=_port + d_vector, angle=deg_port+degree)

        return new_ports

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
        self.ports[name] = handshake(x=ref_port, angle = degree)

    def terminate_port(self, num_port, width=22, gap=6, degree=0, layer='Nb_inv'):
        poly_1 = [-1j * width / 2]
        poly_1.append(1j * width / 2)
        poly_1.append(gap + 1j * width / 2)
        poly_1.append(gap - 1j * width / 2)

        ref_port = self.ports[str(num_port)]
        self.add_geometry(layer, [poly_1], ref=ref_port, degree=degree)
