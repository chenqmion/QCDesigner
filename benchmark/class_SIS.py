from dataclasses import dataclass, field
from class_junction import junction

import numpy as np
import pandas as pd
from pathlib import Path

@dataclass(kw_only=True)
class SIS(junction):
    folder_name: str

    w_um: float | np.ndarray | None = field(init=False, default=None)
    h_um: float | np.ndarray | None = field(init=False, default=None)
    asymmetry: float | np.ndarray | None = field(init=False, default=None)

    def __post_init__(self):
        file_name = 'raw' + self.folder_name[len(self.folder_name.split('_')[0]):] + '.xlsx'
        base_path = Path(__file__).parent / self.folder_name
        df = pd.read_excel(base_path / file_name)

        self.w_um = df['width (um)'].to_numpy()
        self.h_um = df['height (um)'].to_numpy()
        self.asymmetry = df['asymmetry'].to_numpy()
        self.R_Ohm = df['resistance (Ohm)'].to_numpy() / self.asymmetry
        self.x_exp = 1 / (self.w_um * self.h_um)

        super().__post_init__()

    def R2w(self, *, R_goal, h_goal, force_update=False):
        x_goal = self.R2x(R_goal=R_goal, force_update=force_update)
        if h_goal==None:
            w_goal = 1 / np.sqrt(x_goal)
            h_goal = w_goal.copy()
        else:
            w_goal = 1 / (x_goal * h_goal)
        return [w_goal, h_goal]

    def L2w(self, *, L_goal, h_goal, asymmetry, force_update=False):
        if asymmetry == 1:
            R_goal = self.L2R(L=L_goal)
            w_goal, h_goal = self.R2w(R_goal=R_goal, h_goal=h_goal, force_update=force_update)

        else:
            L1 = 2 * L_goal / (1 - asymmetry)
            R1 = self.L2R(L=L1)
            w1, h1 = self.R2w(R_goal=R1, h_goal=h_goal, force_update=force_update)

            if asymmetry == 0:
                w2 = w1.copy()
                h2 = h1.copy()
                R2 = R1.copy()
                L2 = L1.copy()
            else:
                L2 = (1 - asymmetry) / (1 + asymmetry) * L1
                R2 = self.L2R(L=L2)
                w2, h2 = self.R2w(R_goal=R2, h_goal=h_goal, force_update=force_update)

            w_goal = [w1, w2]
            h_goal = [h1, h2]
            R_goal = [R1, R2]
            L_goal = [L1, L2]

        res = {}
        res['w_um'] = w_goal
        res['h_um'] = h_goal
        res['R_Ohm'] = R_goal
        res['L_H'] = L_goal
        return res
