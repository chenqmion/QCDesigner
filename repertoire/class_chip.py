from dataclasses import dataclass, field

import aux_marker
import gdsfactory as gf
import numpy as np

import aux_poly
from class_device import device

@dataclass()
class chip(device):
    name: str = None
    time: str = None
    logo: str = None
    die_size: list[int] = field(default_factory=lambda: [15e3, 15e3])
    chip_size: list[int] = field(default_factory=lambda: [10e3, 10e3])
    trap_size: list[int] = field(default_factory=lambda: [20, 100])

    def __post_init__(self):
        pass
        # poly_1 = []
        # poly_1.append(0)
        # poly_1.append(1j * self.chip_size[1])
        # poly_1.append(self.chip_size[0] + 1j * self.chip_size[1])
        # poly_1.append(self.chip_size[0])
        #
        # poly_2 = []
        # poly_2.append(0)
        # poly_2.append(1j * self.die_size[1])
        # poly_2.append(self.die_size[0] + 1j * self.die_size[1])
        # poly_2.append(self.die_size[0])
        # poly_2 = np.array(poly_2) + (self.chip_size[0] - self.die_size[0]) / 2 + 1j * (
        #             self.chip_size[1] - self.die_size[1]) / 2
        #
        # self.add_geometry('remarks', aux_poly.subtract(poly_2, poly_1), ref=0)

        position_list = [self.chip_size[0] / 3 + 0.4e3 * 1j,
                         self.chip_size[0] / 3 + 1j * (self.chip_size[1] - 0.4e3),
                         self.chip_size[0] * 2 / 3 + 1j * (self.chip_size[1] - 0.4e3)]

        geometry_name = aux_marker.text(self.name, size=2e2)
        self.add_geometry('remarks', geometry_name, ref=position_list[2])

        geometry_time = aux_marker.text(self.time, size=2e2)
        self.add_geometry('remarks', geometry_time, ref=position_list[1])

        geometry_logo = aux_marker.text(self.logo, size=2e2)
        self.add_geometry('remarks', geometry_logo, ref=position_list[0])

    def gen_gds(self, marker=True, flux_trap=False, set_zero=True, merge=False):
        chip_1 = gf.Component()
        chip_layers = list(self.layers.keys())

        geometry_markers = aux_marker.marker(layer_count=len(chip_layers), chip_size=self.chip_size)
        for num_layer, layer in enumerate(chip_layers[:-1]):
            self.add_geometry('remarks', geometry_markers[num_layer])

        protect = gf.Component()

        for num_layer, key_layer in enumerate(chip_layers):
            if (key_layer == 'remarks') and (marker == False):
                pass
            else:
                device_2 = gf.Component()
                device_2.name = key_layer

                val_geometry = self.layers[key_layer]
                for val_poly in val_geometry:
                    if set_zero:
                        val_poly = np.squeeze(val_poly)
                        val_poly += - (self.chip_size[0] / 2 + 1j * self.chip_size[1] / 2)

                    val_poly = np.array([np.real(val_poly), np.imag(val_poly)])
                    idx_layer = np.squeeze(chip_layers.index(key_layer))
                    device_2.add_polygon(val_poly.T, layer=(int(idx_layer), 0))

                    if flux_trap:
                        poly_2 = device_2.get_region(layer=(int(idx_layer), 0))
                        poly_3 = poly_2.size(100 * 1e3)
                        protect.add_polygon(poly_3, layer=(0, 0))

                if merge:
                    device_2.flatten()
                chip_1.add_ref(device_2)

        #%% flux trap
        if (flux_trap == True) and (marker == True):
            trap = gf.Component()

            trap_ = []
            trap_.append(-1 / 2 - 1j / 2)
            trap_.append(-1 / 2 + 1j / 2)
            trap_.append(1 / 2 + 1j / 2)
            trap_.append(1 / 2 - 1j / 2)
            trap_ = np.array(trap_) * self.trap_size[0]

            pt_off = 1.2e3 * (1 + 1j)
            Nx = int((self.chip_size[0] - 2 * np.real(pt_off)) / self.trap_size[1]) + 1
            Ny = int((self.chip_size[1] - 2 * np.imag(pt_off)) / self.trap_size[1]) + 1

            X, Y = np.meshgrid(range(Nx), range(Ny))
            pt_list = pt_off + self.trap_size[1] * (X + 1j * Y).flatten()
            if set_zero:
                pt_list += - (self.chip_size[0] / 2 + 1j * self.chip_size[1] / 2)

            for pt in pt_list:
                val_poly = pt + trap_
                val_poly = np.array([np.real(val_poly), np.imag(val_poly)])
                trap.add_polygon(val_poly.T, layer=(0, 0))

            protect.flatten()
            trap.flatten()
            trap = gf.boolean(trap, protect, operation='not', layer=(0, 0))
            chip_1.add_ref(trap)

        chip_1.name = self.name + '_' + self.time
        chip_1.write_gds(self.name + '_' + self.time + '.gds', with_metadata=False)
        chip_1.show()
