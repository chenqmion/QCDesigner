import os
import sys
import platform

sys.path.append("C:/Users/chenq7/PycharmProjects/QCDComsol/Package/")
from comsol_client import ComsolClient
from comsol_geometry import geometry_mixin
from comsol_material import material_mixin
from comsol_physics import physics_mixin
from comsol_mesh import mesh_mixin
from comsol_study import study_mixin
from comsol_result import result_mixin
from helper_epr import do_epr

#%%
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import scipy.constants as con

phi0 = con.value('mag. flux quantum')/(2*con.pi)

if platform.system() == "Darwin":
    comsol_root = '/Applications/COMSOL63/Multiphysics'
else:
    comsol_root = r'C:\Programs\Comsol'

client = ComsolClient(comsol_root)

# model = client.load_model("fsg_261008_source_1")
# do_epr(model)
#
# model = client.load_model("fsg_261008_source_2")
# do_epr(model)

# model = client.load_model("fsg_261008_source_3")
# do_epr(model)
#
# model = client.load_model("fsg_261008_source_4")
# do_epr(model)

model = client.load_model("fsg_261008")
do_epr(model)
