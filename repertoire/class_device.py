from dataclasses import dataclass, field
import numpy as np
import aux_poly

# %%
@dataclass()
class device():
    ports: dict[complex] = field(default_factory=lambda: {})
    layers: dict[str] = field(default_factory=lambda: {})

    def combine_device(self, device, ref=None, degree=0, axis=None, port=None):
        if port == None:
            ref_port = [0, 0]
        else:
            ref_port = device.ports[port]

        if ref == None:
            d_vector = 0 + 0j
        else:
            d_vector = ref - ref_port[0]

        for num_layer, key_layer in enumerate(list(device.layers.keys())):
            val_geometry = (device.layers[key_layer]).copy()
            self.add_geometry(layer=key_layer, geometry=val_geometry, ref=d_vector, degree=degree, axis=axis,
                              ref_port=ref_port[0])

        # ports
        new_ports = {}
        if len(device.ports) != 0:
            for num_port, key_port in enumerate(list(device.ports.keys())):
                if axis == 'x':
                    val_port = aux_poly.reflect([device.ports[key_port]], axis='x', value=np.imag(ref_port[0]))
                elif axis == 'y':
                    val_port = aux_poly.reflect([device.ports[key_port]], axis='y', value=np.real(ref_port[0]))
                else:
                    val_port = [device.ports[key_port]]

                _port = aux_poly.rotate(val_port, origin=ref_port[0], degree=degree)
                new_ports[key_port] = [_port[0] + d_vector, ref_port[1] + degree]

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
        self.ports[name] = [ref_port, degree]

    def terminate_port(self, num_port, width=22, gap=6, degree=0, layer='Nb_inv'):
        poly_1 = [-1j * width / 2]
        poly_1.append(1j * width / 2)
        poly_1.append(gap + 1j * width / 2)
        poly_1.append(gap - 1j * width / 2)

        ref_port = self.ports[str(num_port)]
        self.add_geometry(layer, [poly_1], ref=ref_port, degree=degree)
