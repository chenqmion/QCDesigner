import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import scipy.constants as con

import os
os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"

import mph

#%%
phi0 = con.value('mag. flux quantum')/(2*con.pi)

LJ1 = 5 # nH
LJ2 = 1 # nH
LJ_list = np.array([LJ1, LJ2]) * 1e-9
EJ_list = (phi0**2)/LJ_list

#%%
mph_file = 'FSG_250612_1'
client = mph.start()
model = client.load(mph_file + '.mph')

#%% inspect model
for (name, value) in model.parameters().items():
    description = model.description(name)
    print(f'{description:20} {name} = {value}')

print(model.physics())
print(model.studies())

#%% modify parameter
Flag_FEM = False

if Flag_FEM:
    while True:
        answer = input('New FEM? [y/n]')
        break

    if (answer != 'y'):
        Flag_FEM = False
        print('Existing FEM loaded')
    else:
        print('FEM started')
        model.parameter('LJ1', str(np.round(LJ1,1))+'[nH]')
        model.parameter('LJ2', str(np.round(LJ2,1))+'[nH]')

        model.build()
        model.mesh()
        model.solve()
        model.save()
        print('FEM finished')
else:
    print('Existing FEM loaded')


#%%
f_list = model.evaluate('emw.freq')
Q_list = model.evaluate('emw.Qfactor')

#%% participation ratio
p_mat = []
phi_mat = []
for num_JJ in range(2):
    val_LJ = LJ_list[num_JJ]
    val_EJ = EJ_list[num_JJ]

    key_I = 'emw.Ielement_' + str(num_JJ+1)
    val_I = model.evaluate(key_I)

    key_We = 'emw.intWe'
    val_We = model.evaluate(key_We)

    val_p = np.sign(np.imag(val_I)) * (np.abs(val_I) ** 2) * val_LJ  / (4*model.evaluate(key_We))
    val_phi = np.sign(np.imag(val_I)) * np.sqrt(np.abs(val_p) * (con.h * f_list)/(2*val_EJ))

    p_mat.append(val_p)
    phi_mat.append(val_phi)

p_mat = np.array(p_mat)
sgn_mat = np.sign(p_mat)
phi_mat = np.array(phi_mat)

#%% Hamiltonian
Chi_mat = np.zeros((len(f_list), len(f_list)))
for num_1 in range(len(f_list)):
    for num_2 in range(len(f_list)):
        Chi_mat[num_1, num_2] = (con.h/4) * f_list[num_1] * f_list[num_2] * np.sum(np.abs(p_mat[:, num_1]) * np.abs(p_mat[:, num_2])/EJ_list)

Delta_list = (1/2) * np.sum(Chi_mat, axis=1)
Alpha_list = (1/2) * np.diag(Chi_mat)

#%%
fig = plt.figure(figsize = (10,12), constrained_layout=True)
gs = GridSpec(nrows=3, ncols=1, figure=fig, height_ratios=[2,1,len(f_list)])

# participation ratio
ax0 = fig.add_subplot(gs[0])
ax0.imshow(p_mat, origin='lower', vmin=-1, vmax=1, cmap='RdBu_r')
for (j,i),label in np.ndenumerate(p_mat):
    label2 = '{:.3f}'.format(label)
    ax0.text(i,j,label2,ha='center',va='center', color='C1')

ax0.set_xticks([])
# ax0.set_xticks(np.linspace(0, len(f_list)-1, len(f_list)),
#            ['{:.3f}'.format(f) for f in f_list/1e9],
#            rotation='vertical')
# ax0.set_xlabel('Eigenfrequency (GHz)')

ax0.set_yticks(np.linspace(0, 1, 2),
           np.linspace(1, 2, 2))
ax0.set_ylabel('Junction')

secax = ax0.secondary_xaxis('top')
secax.set_xticks(np.linspace(0, len(f_list)-1, len(f_list)),
           ['{:.3f}'.format(f) for f in np.sum(np.abs(p_mat), axis=0)],
           rotation='vertical', color='gray')

secay = ax0.secondary_yaxis('right')
secay.set_yticks(np.linspace(0, 1, 2),
                 ['{:.3f}'.format(val) for val in np.sum(np.abs(p_mat), axis=1)],
                 color='gray')

# Delta
ax1 = fig.add_subplot(gs[1])
ax1.imshow([np.log10(Delta_list)], origin='lower', vmin=0, vmax=9, cmap='Blues')
for (j,i),label in np.ndenumerate([Delta_list]):
    label2 = '{:.3f}'.format(label / 1e6)
    ax1.text(i,j,label2,ha='center',va='center', color='C1')

ax1.set_xticks([])
ax1.set_yticks([])
ax1.set_ylabel('Shift')

# Chi
ax2 = fig.add_subplot(gs[2])

Chi_mat2 = Chi_mat.copy()
np.fill_diagonal(Chi_mat2, Alpha_list)

ax2.imshow(np.log10(Chi_mat2), origin='lower', vmin=0, vmax=9, cmap='Blues')
for (j,i),label in np.ndenumerate(Chi_mat2):
    label2 = '{:.3f}'.format(label/1e6)
    ax2.text(i,j,label2,ha='center',va='center', color='C1')

ax2.set_xticks(np.linspace(0, len(f_list)-1, len(f_list)),
           ['{:.3f}'.format(f) for f in f_list/1e9],
           rotation='vertical')
ax2.set_xlabel('Eigenfrequency (GHz)')

ax2.set_yticks(np.linspace(0, len(f_list)-1, len(f_list)),
           ['{:.3f}'.format(f) for f in f_list/1e9])
ax2.set_ylabel('Eigenfrequency (GHz)')

fig.align_ylabels()
plt.savefig(mph_file + '.pdf', bbox_inches='tight')
plt.show()