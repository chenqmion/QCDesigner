import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import scipy.constants as con

import os
os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"

import mph

#%%
phi0 = con.value('mag. flux quantum')/(2*con.pi)

r_cavity = 4.5e-3
h_cavity = 40e-3

r_stub = 1.5e-3
h_stub = 7e-3

#%%
client = mph.start()

model = client.create('stub cavity')
geometries = model/'geometries'
geometry = geometries.create(3, name='geom1')

cavity = geometry.create('Cylinder')
cavity.property('r', r_cavity)
cavity.property('h', h_cavity)

stub = geometry.create('Cylinder')
stub.property('r', r_stub)
stub.property('h', h_stub)

diff1 = model.java.geom("geom1").feature().create("diff1", "Difference")
diff1.selection("input").set("cyl1")
diff1.selection("input2").set("cyl2")
diff1.set("keepsubtract", True)

model.build(geometry)
model.save('model')