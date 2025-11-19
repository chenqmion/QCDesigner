import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import scipy.constants as con

import os
os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"

import mph
#%%
phi0 = con.value('mag. flux quantum')/(2*con.pi)

#%%
client = mph.start()
model = client.create('block of ice')
geometries = model/'geometries'
geometry = geometries.create(3, name='geometry')

block = geometry.create('Block', name='ice block')
block.property('size', ('0.1', '0.2', '0.5'))
model.build(geometry)

model.save('model')