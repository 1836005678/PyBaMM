import pybamm as pb
import numpy as np

pb.set_logging_level("INFO")
# pb.settings.debug_mode = True

options = {"sei": "reaction limited"}
model = pb.lithium_ion.DFN(options)

# experiment = pb.Experiment(
#     [
#         "Discharge at C/10 for 13 hours or until 3.3 V",
#         "Rest for 1 hour",
#         "Charge at 1 A until 4.1 V",
#         "Hold at 4.1 V until 50 mA",
#         "Rest for 1 hour",
#     ]
#     * 10
# )
# experiment = pb.Experiment(["Rest for 20000 hours"])

parameter_values = model.default_parameter_values

# parameter_values.update(
#     {
#         "Inner SEI reaction proportion": 0.5,
#         "Inner SEI partial molar volume [m3.mol-1]": 95.86e-18,
#         "Outer SEI partial molar volume [m3.mol-1]": 95.86e-18,
#         "SEI reaction exchange current density [A.m-2]": 1.5e-6,
#         "SEI resistance per unit thickness [Ohm.m-1]": 1,
#         "Outer SEI solvent diffusivity [m2.s-1]": 2.5e-22,
#         "Bulk solvent concentration [mol.m-3]": 2.636e3,
#         "Ratio of inner and outer SEI exchange current densities": 1,
#         "Inner SEI open-circuit potential [V]": 0.1,
#         "Outer SEI open-circuit potential [V]": 0.8,
#         "Inner SEI electron conducticity [S.m-1]": 8.95e-14,
#         "Inner SEI lithium interstitial diffusivity [m2.s-1]": 1e-15,
#         "Lithium interstitial reference concentration [mol.m-3]": 15,
#         "Initial inner SEI thickness [m]": 7.5e-14,
#     }
# )

# parameter_values.update(
#     {
#         "Inner SEI reaction proportion": 0.5,
#         "Inner SEI partial molar volume [m3.mol-1]": 34.76e-7,
#         "Outer SEI partial molar volume [m3.mol-1]": 34.76e-7,
#         "SEI reaction exchange current density [A.m-2]": 1.5e-7,
#         "SEI resistance per unit thickness [Ohm.m-1]": 1,
#         "Outer SEI solvent diffusivity [m2.s-1]": 2.5e-22,
#         "Bulk solvent concentration [mol.m-3]": 2.636e3,
#         "Ratio of inner and outer SEI exchange current densities": 1,
#         "Inner SEI open-circuit potential [V]": 0.1,
#         "Outer SEI open-circuit potential [V]": 0.8,
#         "Inner SEI electron conducticity [S.m-1]": 8.95e-14,
#         "Inner SEI lithium interstitial diffusivity [m2.s-1]": 1e-15,
#         "Lithium interstitial reference concentration [mol.m-3]": 15,
#         "Initial inner SEI thickness [m]": 7.5e-9,
#         "Initial outer SEI thickness [m]": 7.5e-9,
#     }
# )

# parameter_values.update({"Current function [A]": 0})
parameter_values["Current function [A]"] = "[current data]US06"
parameter_values["Current function [A]"] = 0

sim = pb.Simulation(
    model, parameter_values=parameter_values
)  # , experiment=experiment)

solver = pb.CasadiSolver(mode="fast")

years = 3
days = years * 365
hours = days * 24
minutes = hours * 60
seconds = minutes * 60
t_eval = np.linspace(0, seconds, 100)

# sim.solve(solver=solver)
sim.solve(solver=solver, t_eval=t_eval)
sim.plot(
    [
        "Terminal voltage [V]",
        "Total SEI thickness [m]",
        "X-averaged total SEI thickness [m]",
        "X-averaged total SEI thickness",
        "X-averaged SEI concentration [mol.m-3]",
        "Loss of lithium to SEI [mols]",
        "SEI reaction interfacial current density [A.m-2]",
        "X-averaged SEI reaction interfacial current density [A.m-2]",
    ]
)
