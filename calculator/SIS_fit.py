import matplotlib.pyplot as plt
import numpy as np

plt.rcParams.update({'font.size': 7})
cm = 1 / 2.54
plt.rcParams['axes.prop_cycle'] = plt.cycler(color=plt.get_cmap('Set1').colors)

import pandas as pd
from pathlib import Path

import Toolkit_SIS as TSIS

# %%
file_name = 'raw_250717.xlsx'
base_path = Path(__file__).parent / 'data_resistance'
df = pd.read_excel(base_path / file_name)

order = 3
mode = 'log'

w_list = df['width (um)']
h_list = df['height (um)']
x_list = 1 / (w_list * h_list).to_numpy()

R_list = (df['resistance (Ohm)'] * df['number']).to_numpy()
L_list = TSIS.R2L(R_list)

cmap_list = np.array(['C0', 'C1'])
color_list = cmap_list[(df['number'].to_numpy() - 1).astype(int)]

poly_coe = TSIS.fit_R(x_list, R_list, order=order, mode=mode)

# %% plots
res_1 = TSIS.L2w(5.2e-9, poly_coe, mode=mode, asy=1)

R_sim = np.linspace(5e2, 1e5, int(1e3))
x_sim = TSIS.get_x(R_sim, poly_coe, mode=mode)
L_sim = TSIS.R2L(R_sim)

fig, ax = plt.subplots(figsize=(12 * cm, 12 * cm))
ax2 = ax.twinx()
ax2.get_yaxis().set_visible(False)

ax.scatter(x_list, L_list, c=color_list)
ax.plot(x_sim, L_sim, color='k')

ax.scatter(1/res_1[0]**2, res_1[1], color='C5', marker='*', s=100)

ax.set_xscale('log')
ax.set_yscale('log')
ax2.set_yscale('log')

# ax.legend(loc=(0.5,0.3))
# ax2.legend(loc=(0.5,0.05))

ax.set_ylabel(r'$L_{\rm J}\,({\rm H})$')
ax.set_xlabel(r'$1/w_{\rm J}^{2}\,({\rm 1/\mu m^2})$')

secax = ax.secondary_yaxis('right', functions=(TSIS.L2R, TSIS.R2L))
secax.set_ylabel(r'$R_{\rm J}\,({\rm \Omega})$')

plt.savefig(base_path / (file_name[:-4] + 'pdf'), dpi=300, bbox_inches='tight')
plt.show()
