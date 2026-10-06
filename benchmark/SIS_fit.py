from config_plot import plt, cm

import numpy as np
import scipy as sci
import scipy.constants as con

import pandas as pd
from pathlib import Path

from class_SIS import SIS

# %%
# folder_name = 'SIS_250717'
# folder_name = 'Wavepool_260811_v1'
folder_name = 'Wavepool_260811_v2'
file_name = 'raw' + folder_name[len(folder_name.split('_')[0]):] + '.xlsx'
base_path = Path(__file__).parent / folder_name

order = 1
mode = 'log'
# gap = 179.4E-6 * con.e
gap = 217E-6 * con.e # thin film

SIS_exp = SIS(folder_name=folder_name, gap_V=gap, poly_mode = mode, poly_order = order)
cmap_list = np.array(['C0', 'C1'])
color_list = cmap_list[(2-2*SIS_exp.asymmetry).astype(int)]

#%%
L_goal = 5.2e-9
res_1 = SIS_exp.L2w(L_goal=L_goal, h_goal=None, asymmetry=1, force_update=False)
print(res_1)

# %% plots
R_sim = np.linspace(5e2, 1e5, int(1e3))
x_sim = SIS_exp.R2x(R_goal=R_sim)
L_sim = SIS_exp.R2L(R=R_sim)

fig, ax = plt.subplots(figsize=(12 * cm, 12 * cm))

ax.scatter(SIS_exp.x_exp, SIS_exp.L_H, c=color_list)
ax.plot(x_sim, L_sim, color='k')

ax.scatter(1/res_1['w_um']**2, res_1['L_H'], color='C2', marker='*', s=100, zorder=1000)

ax.set_xscale('log')
ax.set_yscale('log')

ax.set_ylabel(r'$L_{\rm J}\,({\rm H})$')
ax.set_xlabel(r'$1/\text{area}\,({\rm \mu m^{-2}})$')
ax.set_ylim(2e-10, 2e-7)

secax = ax.secondary_yaxis('right',
                           functions=(lambda l: SIS_exp.L2R(L=l),
                                      lambda r: SIS_exp.R2L(R=r))
                           )
secax.set_ylabel(r'$R_{\rm J}\,({\rm \Omega})$')

plt.savefig(base_path / (file_name[:-4] + 'pdf'), dpi=300, bbox_inches='tight')
plt.show()
