from dataclasses import dataclass, field
from class_junction import junction

import numpy as np
import pandas as pd
from pathlib import Path

@dataclass(kw_only=True)
class SNS(junction):
    folder_name: str

    w_um: float | np.ndarray | None = field(init=False, default=None)
    t_um: float | np.ndarray | None = field(init=False, default=None)
    l_um: float | np.ndarray | None = field(init=False, default=None)

    def __post_init__(self):
        file_name = 'raw' + self.folder_name[len(self.folder_name.split('_')[0]):] + '.xlsx'
        base_path = Path(__file__).parent / self.folder_name
        df = pd.read_excel(base_path / file_name)

        self.w_um = df['width (um)'].to_numpy()
        self.t_um = df['thickness (um)'].to_numpy()
        self.l_um = df['length (um)'].to_numpy()
        self.R_Ohm = df['resistance (Ohm)'].to_numpy()
        self.x_exp = self.l_um / (self.w_um * self.t_um)

        super().__post_init__()

    def R2l(self, *, R_goal, w_goal, t_goal, force_update=False):
        x_goal = self.R2x(R_goal=R_goal, force_update=force_update)
        l_goal = x_goal * (w_goal * t_goal)
        return l_goal

    def L2l(self, *, L_goal, w_goal, t_goal, force_update=False):
        R_goal = self.L2R(L=L_goal)
        l_goal = self.R2l(R_goal=R_goal, w_goal=w_goal, t_goal=t_goal, force_update=force_update)

        res = {}
        res['l_um'] = l_goal
        res['w_um'] = w_goal
        res['t_um'] = t_goal
        res['R_Ohm'] = R_goal
        res['L_H'] = L_goal
        return res
