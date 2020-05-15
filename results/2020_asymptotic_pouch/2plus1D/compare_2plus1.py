import pybamm
import numpy as np
import os
import sys
import pickle
import matplotlib
import matplotlib.pyplot as plt
import shared

# change working directory to the root of pybamm
os.chdir(pybamm.root_dir())

# set style
matplotlib.rc_file(
    "results/2019_xx_2plus1D_pouch/_matplotlibrc", use_default_template=True
)

# increase recursion limit for large expression trees
sys.setrecursionlimit(100000)

pybamm.set_logging_level("INFO")


"-----------------------------------------------------------------------------"
"Load comsol data"

try:
    comsol_variables = pickle.load(
        open("input/comsol_results/comsol_thermal_2plus1D_1C.pickle", "rb")
    )
except FileNotFoundError:
    raise FileNotFoundError("COMSOL data not found. Try running load_comsol_data.py")


"-----------------------------------------------------------------------------"
"Set up and solve pybamm simulation"

# model
options = {"current collector": "potential pair", "dimensionality": 2}
pybamm_model = pybamm.lithium_ion.DFN(options)

# parameters
param = pybamm_model.default_parameter_values
param.update({"C-rate": 1})

# set mesh
var = pybamm.standard_spatial_vars
submesh_types = pybamm_model.default_submesh_types
var_pts = {
    var.x_n: 5,
    var.x_s: 5,
    var.x_p: 5,
    var.r_n: 10,
    var.r_p: 10,
    var.y: 14,
    var.z: 9,
}

# solver
solver = pybamm.CasadiSolver(
    atol=1e-6, rtol=1e-6, root_tol=1e-3, root_method="krylov", mode="fast"
)

# simulation object
simulation = pybamm.Simulation(
    pybamm_model,
    parameter_values=param,
    submesh_types=submesh_types,
    var_pts=var_pts,
    solver=solver,
)

# build simulation
simulation.build(check_model=False)

# discharge timescale
tau = param.evaluate(pybamm.standard_parameters_lithium_ion.tau_discharge)

# solve model at comsol times
t_eval = comsol_variables["time"] / tau
simulation.solve(t_eval=t_eval)


"-----------------------------------------------------------------------------"
"Make Comsol 'model' for comparison"

# interpolate using *dimensional* space. Note that both y and z are scaled with L_z
mesh = simulation._mesh
L_z = param.evaluate(pybamm.standard_parameters_lithium_ion.L_z)
pybamm_y = mesh["current collector"][0].edges["y"]
pybamm_z = mesh["current collector"][0].edges["z"]
y_interp = pybamm_y * L_z
z_interp = pybamm_z * L_z

comsol_model = shared.make_comsol_model(
    comsol_variables, mesh, param, y_interp=y_interp, z_interp=z_interp, thermal=False
)

# Process pybamm variables for which we have corresponding comsol variables
output_variables = simulation.post_process_variables(
    list(comsol_model.variables.keys())
)

"-----------------------------------------------------------------------------"
"Make plots"

t_plot = 1800  # dimensional in seconds
shared.plot_cc_potentials(t_plot, comsol_model, output_variables, param)
plt.savefig("isothermal2plus1D_cc_pots.pdf", format="pdf", dpi=1000)
shared.plot_cc_current(t_plot, comsol_model, output_variables, param)
plt.savefig("isothermal2plus1D_cc_current.pdf", format="pdf", dpi=1000)
plt.show()
