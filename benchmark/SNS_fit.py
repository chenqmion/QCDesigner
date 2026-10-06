from config_plot import plt, cm

import numpy as np
import scipy as sci
import scipy.constants as con

import pandas as pd
from pathlib import Path

from class_SNS import SNS

# %%
# folder_name = 'SNS_250717'
folder_name = 'SNS_250809'
file_name = 'raw' + folder_name[3:] + '.xlsx'
base_path = Path(__file__).parent / folder_name

order = 1
mode = 'log'
# gap = 59.3E-6 * con.e # bulk
gap = 15.2E-6 * con.e # thin film

SNS_exp = SNS(folder_name=folder_name, gap_V=gap, poly_mode=mode, poly_order = order)

#%%
L_goal = 1e-9
res_1 = SNS_exp.L2l(L_goal=L_goal, w_goal=0.15, t_goal=0.05, force_update=False)
print(res_1)

# %% plots
R_sim = np.linspace(5e1, 2e3, int(1e3))
x_sim = SNS_exp.R2x(R_goal=R_sim)
L_sim = SNS_exp.R2L(R=R_sim)

fig, ax = plt.subplots(figsize=(12 * cm, 12 * cm))

ax.scatter(SNS_exp.x_exp, SNS_exp.L_H)
ax.plot(x_sim, L_sim, color='k')

ax.scatter(res_1['l_um']/(res_1['w_um']*res_1['t_um']), res_1['L_H'], color='C2', marker='*', s=100, zorder=1000)

ax.set_xscale('log')
ax.set_yscale('log')

ax.set_ylabel(r'$L_{\rm J}\,({\rm H})$')
ax.set_xlabel(r'$\text{length}/\text{area}\,({\rm \mu m^{-1}})$')
ax.set_ylim(2e-10, 2e-7)

secax = ax.secondary_yaxis('right',
                           functions=(lambda l: SNS_exp.L2R(L=l),
                                      lambda r: SNS_exp.R2L(R=r))
                           )
secax.set_ylabel(r'$R_{\rm J}\,({\rm \Omega})$')

plt.savefig(base_path / (file_name[:-4] + 'pdf'), dpi=300, bbox_inches='tight')
plt.show()