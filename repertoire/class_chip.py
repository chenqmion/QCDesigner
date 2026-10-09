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
        position_list = [self.chip_size[0] / 3 + 0.4e3 * 1j,
                         self.chip_size[0] / 3 + 1j * (self.chip_size[1] - 0.4e3),
                         self.chip_size[0] * 2 / 3 + 1j * (self.chip_size[1] - 0.4e3)]

        geometry_name = aux_marker.text(self.name, size=2e2)
        self.add_geometry('remarks', geometry_name, ref=position_list[2])

        geometry_time = aux_marker.text(self.time, size=2e2)
        self.add_geometry('remarks', geometry_time, ref=position_list[1])

        geometry_logo = aux_marker.text(self.logo, size=2e2)
        self.add_geometry('remarks', geometry_logo, ref=position_list[0])

    def gen_gds(self, marker=True, flux_trap=False, set_zero=True, merge=False, show=True):
        gf.clear_cache()

        layers = {k: list(v) for k, v in self.layers.items()}
        chip_layers = list(layers.keys())

        if marker:
            geometry_markers = aux_marker.marker(layer_count=len(chip_layers),
                                                 chip_size=self.chip_size)
            for num_layer in range(len(chip_layers) - 1):
                layers.setdefault('remarks', [])
                layers['remarks'] += [list(np.ravel(p)) for p in geometry_markers[num_layer]]

        chip_1 = gf.Component()
        protect = gf.Component()
        offset = (self.chip_size[0] / 2 + 1j * self.chip_size[1] / 2)

        # ---- 各层几何 ----
        for key_layer in chip_layers:
            if (key_layer == 'remarks') and (not marker):
                continue

            idx_layer = int(chip_layers.index(key_layer))
            device_2 = gf.Component()
            device_2.name = key_layer

            for val_poly in layers[key_layer]:
                val_poly = np.squeeze(np.asarray(val_poly, dtype=complex))
                if set_zero:
                    val_poly = val_poly - offset
                xy = np.array([np.real(val_poly), np.imag(val_poly)])
                device_2.add_polygon(xy.T, layer=(idx_layer, 0))

            # protect：每层只做一次（关键——移出内层逐多边形循环，O(M) 而非 O(M^2)）
            if flux_trap:
                region = device_2.get_region(layer=(idx_layer, 0))
                region = region.size(50 * 1e3)        # 整层电路外扩 50 µm 的保护圈
                protect.add_polygon(region, layer=(0, 0))

            if merge:
                device_2.flatten()
            chip_1.add_ref(device_2)

        # ---- flux trap 网格 ----
        if flux_trap and marker:
            trap = gf.Component()
            trap_ = np.array([-0.5 - 0.5j, -0.5 + 0.5j, 0.5 + 0.5j, 0.5 - 0.5j]) * self.trap_size[0]

            pt_off = 650 * (1 + 1j)
            Nx = int((self.chip_size[0] - 2 * np.real(pt_off)) / self.trap_size[1]) + 1
            Ny = int((self.chip_size[1] - 2 * np.imag(pt_off)) / self.trap_size[1]) + 1

            X, Y = np.meshgrid(range(Nx), range(Ny))
            pt_list = pt_off + self.trap_size[1] * (X + 1j * Y).flatten()
            if set_zero:
                pt_list = pt_list - offset

            for pt in pt_list:
                vp = pt + trap_
                trap.add_polygon(np.array([np.real(vp), np.imag(vp)]).T, layer=(0, 0))

            protect.flatten()
            trap.flatten()
            trap = gf.boolean(trap, protect, operation='not', layer=(0, 0))
            chip_1.add_ref(trap)

        # ---- 输出 ----
        chip_1.name = self.name + '_' + self.time
        chip_1.write_gds(self.name + '_' + self.time + '.gds', with_metadata=False)

        if show:
            try:
                chip_1.show()
            except Exception as e:
                print(f'[gen_gds] show() 已跳过（KLayout/klive 未连接）: {e}')

        return chip_1