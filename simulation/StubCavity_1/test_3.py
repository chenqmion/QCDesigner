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
model.component("comp1").geom().create("geom1", 3)

#%% geometry
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

#%% material
model.component("comp1").material().create("mat1", "Common")
model.material("mat1").propertyGroup("def").set("relpermittivity", "1")
model.material("mat1").propertyGroup("def").set("relpermeability", "1")
model.material("mat1").propertyGroup("def").set("electricconductivity", "0")
# model.material("mat1").selection().set(1)

#%% physics
model.component("comp1").physics().create("emw", "ElectromagneticWaves", "geom1")
model.physics("emw").selection().set(1)

#%% mesh
model.component("comp1").mesh().create("mesh1")
model.mesh("mesh1").autoMeshSize(5)
model.mesh("mesh1").run()

#%% study
model.study().create("std1")
model.study("std1").feature().create("eig", "Eigenfrequency")
model.study("std1").feature("eig").set('shift', "5[GHz]")
model.study("std1").feature("eig").set('neigs', "10")
model.study("std1").feature("eig").set('eigwhich', 'lr')

# model.study("std1").run()
model.study("std1").createAutoSequences("all")
model.sol("sol1").runAll()

#%% plot
# model.result("pg1").run()

#%%
pymodel.save('model')