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
h_cavity = 50e-3

r_stub = 1.5e-3
h_stub = 15e-3

r_pin = 0.5e-3
r_bulk = 1.15e-3

z_cavity_drive = 20e-3
l_cavity_drive_1 = r_cavity + 5e-3
l_cavity_drive_2 = 2e-3

z_tube = np.copy(h_stub)
r_tube = 2e-3
l_tube = r_cavity + 25e-3

x_qubit_drive = r_cavity + 10e-3
l_qubit_drive_1 = r_tube + 5e-3
l_qubit_drive_2 = 2e-3

z_output = z_tube + 0.85e-3
l_output_1 = 5e-3
l_output_2 = 2e-3

#%%
client = mph.start()
pymodel = client.create('Model')
model = pymodel.java

model.modelNode().create("comp1")
model.component("comp1").geom().create("geom1", 3)

#%% geometry
model.geom("geom1").feature().create("cyl_cavity", "Cylinder")
model.geom("geom1").feature("cyl_cavity").set('r', r_cavity)
model.geom("geom1").feature("cyl_cavity").set('h', h_cavity)

model.geom("geom1").feature().create("cyl_stub", "Cylinder")
model.geom("geom1").feature("cyl_stub").set('r', r_stub)
model.geom("geom1").feature("cyl_stub").set('h', h_stub)

# cavity drive
model.geom("geom1").feature().create("cyl_cavity_drive1", "Cylinder")
model.geom("geom1").feature("cyl_cavity_drive1").set('axistype', 'x')
model.geom("geom1").feature("cyl_cavity_drive1").set("pos", [-l_cavity_drive_1, 0, z_cavity_drive])
model.geom("geom1").feature("cyl_cavity_drive1").set('r', r_bulk)
model.geom("geom1").feature("cyl_cavity_drive1").set('h', l_cavity_drive_1)

model.geom("geom1").feature().create("cyl_cavity_drive2", "Cylinder")
model.geom("geom1").feature("cyl_cavity_drive2").set('axistype', 'x')
model.geom("geom1").feature("cyl_cavity_drive2").set("pos", [-l_cavity_drive_1, 0, z_cavity_drive])
model.geom("geom1").feature("cyl_cavity_drive2").set('r', r_pin)
model.geom("geom1").feature("cyl_cavity_drive2").set('h', l_cavity_drive_2)

# chip tube
model.geom("geom1").feature().create("cyl_tube", "Cylinder")
model.geom("geom1").feature("cyl_tube").set('axistype', 'x')
model.geom("geom1").feature("cyl_tube").set("pos", [0, 0, z_tube])
model.geom("geom1").feature("cyl_tube").set('r', r_tube)
model.geom("geom1").feature("cyl_tube").set('h', l_tube)

# qubit drive
model.geom("geom1").feature().create("cyl_qubit_drive1", "Cylinder")
model.geom("geom1").feature("cyl_qubit_drive1").set("pos", [x_qubit_drive, 0, z_tube])
model.geom("geom1").feature("cyl_qubit_drive1").set('r', r_bulk)
model.geom("geom1").feature("cyl_qubit_drive1").set('h', l_qubit_drive_1)

model.geom("geom1").feature().create("cyl_qubit_drive2", "Cylinder")
model.geom("geom1").feature("cyl_qubit_drive2").set("pos", [x_qubit_drive, 0, z_tube + l_qubit_drive_1 - l_qubit_drive_2])
model.geom("geom1").feature("cyl_qubit_drive2").set('r', r_pin)
model.geom("geom1").feature("cyl_qubit_drive2").set('h', l_qubit_drive_2)

# output
model.geom("geom1").feature().create("cyl_output1", "Cylinder")
model.geom("geom1").feature("cyl_output1").set('axistype', 'x')
model.geom("geom1").feature("cyl_output1").set("pos", [l_tube, 0, z_output])
model.geom("geom1").feature("cyl_output1").set('r', r_bulk)
model.geom("geom1").feature("cyl_output1").set('h', l_output_1)

model.geom("geom1").feature().create("cyl_output2", "Cylinder")
model.geom("geom1").feature("cyl_output2").set('axistype', 'x')
model.geom("geom1").feature("cyl_output2").set("pos", [l_tube + (l_output_1 - l_output_2), 0, z_output])
model.geom("geom1").feature("cyl_output2").set('r', r_pin)
model.geom("geom1").feature("cyl_output2").set('h', l_output_2)

# combine
model.geom("geom1").feature().create("diff1", "Difference")
model.geom("geom1").feature("diff1").selection("input").set("cyl_cavity", "cyl_tube", "cyl_cavity_drive1", "cyl_qubit_drive1", "cyl_output1")
model.geom("geom1").feature("diff1").selection("input2").set("cyl_stub", "cyl_cavity_drive2", "cyl_qubit_drive2", "cyl_output2")
model.geom("geom1").feature("diff1").set("keepsubtract", True)
model.geom("geom1").feature("diff1").set("intbnd", False)

model.geom("geom1").run("fin")

# #%% material
# model.component("comp1").material().create("mat1", "Common")
# model.material("mat1").propertyGroup("def").set("relpermittivity", "1")
# model.material("mat1").propertyGroup("def").set("relpermeability", "1")
# model.material("mat1").propertyGroup("def").set("electricconductivity", "0")
# # model.material("mat1").selection().set(1)
#
# #%% physics
# model.component("comp1").physics().create("emw", "ElectromagneticWaves", "geom1")
# model.physics("emw").selection().set(1)
#
# #%% mesh
# model.component("comp1").mesh().create("mesh1")
# model.mesh("mesh1").autoMeshSize(5)
# model.mesh("mesh1").run()
#
# #%% study
# model.study().create("std1")
# model.study("std1").feature().create("eig", "Eigenfrequency")
# model.study("std1").feature("eig").set('shift', "5[GHz]")
# model.study("std1").feature("eig").set('neigs', "10")
# model.study("std1").feature("eig").set('eigwhich', 'lr')
#
# # model.study("std1").run()
# model.study("std1").createAutoSequences("all")
# model.sol("sol1").runAll()

#%% plot
# model.result("pg1").run()

#%%
pymodel.save('model')