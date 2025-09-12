from dataclasses import dataclass

import gdsfactory as gf
import numpy as np


# %%
def poly_rotate(poly, origin=(0 + 0j), degree=0):
    poly_new = []
    for point in poly:
        vec = np.subtract(point, origin)
        poly_new.append(origin + vec * np.exp(1j * degree * np.pi / 180))
    return np.array(poly_new)


def poly_reflect(poly, axis='x', value=0):
    poly_new = []
    for point in poly:
        if axis == 'x':
            poly_new.append(np.real(point) + 1j * (2 * value - np.imag(point)))
        else:
            poly_new.append((2 * value - np.real(point)) + 1j * np.imag(point))
    return np.array(poly_new)


def poly_hole(poly_1, poly_2):
    poly_1_new = list(poly_1) + [poly_1[0]]
    poly_2_new = list(poly_2) + [poly_2[0]]
    poly_1_new += poly_2_new[::-1]

    return np.array(poly_1_new)


# %%
@dataclass()
class device():
    name: str = None
    ports: dict = None
    layers: dict = None

    def combine_device(self, device, ref=(0 + 0j), degree=0, axis='none', port=1):
        if self.layers is None:
            self.layers = {}

        if device.ports == None:
            device.add_port(1, 0)

        ref_port = device.ports[str(port)]
        # d_vector = ref - ref_port
        if np.abs(ref) == 0:
            d_vector = 0 + 0j
        else:
            d_vector = ref - ref_port

        for num_layer, key_layer in enumerate(list(device.layers.keys())):
            val_geometry = (device.layers[key_layer]).copy()
            self.add_geometry(layer=key_layer, geometry=val_geometry, ref=d_vector, degree=degree, axis=axis,
                              ref_port=ref_port)

        # ports
        new_ports = {}
        for num_port, key_port in enumerate(list(device.ports.keys())):
            if axis == 'x':
                val_port = poly_reflect([device.ports[key_port]], axis='x', value=np.imag(ref_port))
            elif axis == 'y':
                val_port = poly_reflect([device.ports[key_port]], axis='y', value=np.real(ref_port))
            else:
                val_port = [device.ports[key_port]]

            _port = poly_rotate(val_port, origin=ref_port, degree=degree)
            new_ports[key_port] = _port[0] + d_vector

        return new_ports

    def add_geometry(self, layer, geometry, ref=(0 + 0j), degree=0, axis='none', ref_port=0):
        if self.layers is None:
            self.layers = {}

        geometry2 = []
        for num_poly, val_poly in enumerate(geometry):
            if axis == 'x':
                val_poly = poly_reflect(val_poly, axis='x', value=np.imag(ref_port))
            elif axis == 'y':
                val_poly = poly_reflect(val_poly, axis='y', value=np.real(ref_port))

            val_poly = poly_rotate(val_poly, origin=ref_port, degree=degree)
            val_poly = list(val_poly + ref)
            geometry2.append(val_poly)

        if layer in list(self.layers.keys()):
            self.layers[layer] += geometry2
        else:
            self.layers[layer] = geometry2

    def add_port(self, num_port, ref_port):
        if self.ports is None:
            self.ports = {}

        self.ports[str(num_port)] = complex(ref_port)

    def terminate_port(self, num_port, width=22, gap=6, degree=0, layer='Nb_inv'):
        poly_1 = [-1j * width / 2]
        poly_1.append(1j * width / 2)
        poly_1.append(gap + 1j * width / 2)
        poly_1.append(gap - 1j * width / 2)

        ref_port = self.ports[str(num_port)]
        self.add_geometry(layer, [poly_1], ref=ref_port, degree=degree)


@dataclass(kw_only=True)
class chip(device):
    name: str
    time: str
    logo: str
    chip_size: tuple = (15e3, 15e3)
    gnd_size: tuple = (10e3, 10e3)
    trap_params: tuple = (20, 100)

    def add_device(self, device, ref=(0 + 0j), degree=0, axis='none', port=1):
        new_ports = self.combine_device(device, ref=ref, degree=degree, axis=axis, port=port)
        return new_ports

    def set_zero(self):
        for key_layer in self.layers.keys():
            geometry_list_new = []
            for num_ploy, poly in enumerate(self.layers[key_layer]):
                geometry_list_new.append(np.squeeze(poly) - (self.chip_size[0] / 2 + 1j * self.chip_size[1] / 2))
            self.layers[key_layer] = geometry_list_new

    def gen_gds(self, flux_trap=False):
        chip = gf.Component()

        protect = gf.Component()
        for num_layer, key_layer in enumerate(list(self.layers.keys())):
            val_geometry = self.layers[key_layer]

            device = gf.Component()
            device.name = key_layer
            for val_poly in val_geometry:
                val_poly = np.array([np.real(val_poly), np.imag(val_poly)])
                device.add_polygon(val_poly.T, layer=(num_layer, 0))

            # device.flatten()
            chip.add_ref(device)

            if flux_trap:
                poly_2 = device.get_region(layer=(num_layer, 0))
                poly_3 = poly_2.size(100 * 1e3)
                protect.add_polygon(poly_3, layer=(len(self.layers), 0))

        if flux_trap:
            trap = gf.Component()

            trap_ = []
            trap_.append(-1 / 2 - 1j / 2)
            trap_.append(-1 / 2 + 1j / 2)
            trap_.append(1 / 2 + 1j / 2)
            trap_.append(1 / 2 - 1j / 2)
            trap_ = np.array(trap_) * self.trap_params[0]

            pt_off = -(self.gnd_size[0] - 2 * 1.2e3) / 2 - 1j * (self.gnd_size[1] - 2 * 1.2e3) / 2
            Nx = int((self.gnd_size[0] - 2 * 1.2e3) / self.trap_params[1]) + 1
            Ny = int((self.gnd_size[1] - 2 * 1.2e3) / self.trap_params[1]) + 1

            X, Y = np.meshgrid(range(Nx), range(Ny))
            pt_list = pt_off + self.trap_params[1] * (X + 1j * Y).flatten()
            for pt in pt_list:
                val_poly = pt + trap_
                val_poly = np.array([np.real(val_poly), np.imag(val_poly)])
                trap.add_polygon(val_poly.T, layer=(len(self.layers), 0))

            protect.flatten()
            trap.flatten()
            trap = gf.boolean(trap, protect, operation='not', layer=(len(self.layers), 0))
            chip.add_ref(trap)

        chip.name = self.name
        chip.write_gds('chip_' + self.name + '_' + self.time + '.gds', with_metadata=False)
        chip.show()
