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
pymodel = client.create('Model')
model = pymodel.java

model.modelNode().create("comp1")
model.geom().create("geom1", 3)

model.geom("geom1").feature().create("cyl1", "Cylinder")
model.geom("geom1").feature("cyl1").set('r', r_cavity)
model.geom("geom1").feature("cyl1").set('h', h_cavity)

model.geom("geom1").feature().create("cyl2", "Cylinder")
model.geom("geom1").feature("cyl2").set('r', r_stub)
model.geom("geom1").feature("cyl2").set('h', h_stub)

model.geom("geom1").feature().create("diff1", "Difference")
model.geom("geom1").feature("diff1").selection("input").set("cyl1")
model.geom("geom1").feature("diff1").selection("input2").set("cyl2")
model.geom("geom1").feature("diff1").set("keepsubtract", True)

model.geom("geom1").run("fin")

pymodel.save('model')