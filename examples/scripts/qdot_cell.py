import pybamm as pb
import numpy as np
import matplotlib.pyplot as plt

pb.set_logging_level("INFO")

load = False

c_rate = 1
filename = "qdot_" + str(c_rate) + "C.p"

options = {
    # "current collector": "potential pair",
    # "dimensionality": 2,
    "thermal": "x-lumped",
}
model = pb.lithium_ion.DFN(options)

chemistry = pb.parameter_sets.NCA_Kim2011
parameter_values = pb.ParameterValues(chemistry=chemistry)

number_of_layer = 48
# 5 C rate is 100A per cell and 75A/m^2 per layer. So is 2.1 A per layer. 100 / 2.1 = 48 layers

kim_set = {
    "Cell capacity [A.h]": 0.43,
    "Typical current [A]": 1,
    "C-rate": c_rate,
    "Electrode height [m]": 0.2,
    "Electrode width [m]": 0.14,
    "Positive tab width [m]": 0.044000000000000004,
    "Negative tab width [m]": 0.044000000000000004,
    "Negative tab centre y-coordinate [m]": 0.013000000000000001,
    "Negative tab centre z-coordinate [m]": 0.2,
    "Positive tab centre y-coordinate [m]": 0.13699999999999998,
    "Positive tab centre z-coordinate [m]": 0.2,
    "Upper voltage cut-off [V]": 4.5,
    "Lower voltage cut-off [V]": 2.5,
    "Heat transfer coefficient [W.m-2.K-1]": 0,  # 0.260,
    "Cation transference number": 0.5,  # makes no difference to heat gen
}
# for heat transfer lump cooling on 1 side of battery across 48 layers.
# So h = 25 / 2 / 48

qdot_set = {
    "Cell capacity [A.h]": 0.43,
    "Typical current [A]": 0.43,
    "Electrode height [m]": 0.2,
    "Electrode width [m]": 0.14,
    "Positive tab width [m]": 0.044000000000000004,
    "Negative tab width [m]": 0.044000000000000004,
    "Negative tab centre y-coordinate [m]": 0.013000000000000001,
    "Negative tab centre z-coordinate [m]": 0.2,
    "Positive tab centre y-coordinate [m]": 0.13699999999999998,
    "Positive tab centre z-coordinate [m]": 0.2,
    "Upper voltage cut-off [V]": 4.5,
    "Lower voltage cut-off [V]": 2.7,
}

parameter_values.update(kim_set)

parameter_values = model.default_parameter_values
parameter_values.update({"Heat transfer coefficient [W.m-2.K-1]": 0})

var = pb.standard_spatial_vars
var_pts = {
    var.x_n: 5,
    var.x_s: 5,
    var.x_p: 5,
    var.r_n: 5,
    var.r_p: 5,
    var.y: 5,
    var.z: 5,
}

solver = pb.CasadiSolver(mode="safe")

if load is True:
    sim = pb.load(filename)
elif load is False:
    sim = pb.Simulation(
        model,
        parameter_values=parameter_values,
        var_pts=var_pts,
        solver=solver,
        C_rate=c_rate,
    )
    if c_rate == 1:
        t_eval = np.linspace(0, 0.32, 100)
    elif c_rate == 5:
        t_eval = np.linspace(0, 0.048, 100)
        # t_eval = np.linspace(0, 0.04, 100)
    # t_eval = np.linspace(0, 0.02, 100)
    sim.solve(t_eval=t_eval)
    sim.save(filename)

# plotting
plot_variables = [
    "Time [h]",
    "Discharge capacity [A.h]",
    "Terminal voltage [V]",
    "X-averaged negative particle surface concentration",
    "X-averaged positive particle surface concentration",
    "X-averaged cell temperature [K]",
    "Volume-averaged cell temperature [K]",
    "Volume-averaged total heating [W.m-3]",
    "Current collector current density [A.m-2]",
]

built_model = sim.built_model
variables = built_model.variables
sol = sim.solution
t = sol.t

print("Final dimensionless time is " + str(t[-1]))

l_n = parameter_values.process_symbol(pb.standard_parameters_lithium_ion.l_n).evaluate()
l_s = parameter_values.process_symbol(pb.standard_parameters_lithium_ion.l_s).evaluate()
l_p = parameter_values.process_symbol(pb.standard_parameters_lithium_ion.l_p).evaluate()

l_y = parameter_values.process_symbol(pb.standard_parameters_lithium_ion.l_y).evaluate()
l_z = parameter_values.process_symbol(pb.standard_parameters_lithium_ion.l_z).evaluate()
L_y = parameter_values.process_symbol(pb.standard_parameters_lithium_ion.L_y).evaluate()
L_z = parameter_values.process_symbol(pb.standard_parameters_lithium_ion.L_z).evaluate()

cell_volume = 0.00021  # m3

x_n = np.linspace(0, l_n, 100)
x_s = np.linspace(0, l_s, 100)
x_p = np.linspace(0, l_p, 100)

y = np.linspace(0, l_y, 20)
z = np.linspace(0, l_z, 20)

sim.plot(["X-averaged positive particle concentration"])

processed_variables = {}
for var in plot_variables:
    processed_variables[var] = pb.ProcessedVariable(variables[var], sol)

# plot terminal voltage
plt.plot(
    processed_variables["Time [h]"](t), processed_variables["Terminal voltage [V]"](t)
)
plt.xlabel("Time [h]")
plt.ylabel("Terminal voltage [V]")
plt.show()

plt.plot(
    processed_variables["Discharge capacity [A.h]"](t),
    processed_variables["Terminal voltage [V]"](t),
)
plt.xlabel("Discharge capacity [A.h] (1 layer)")
plt.ylabel("Terminal voltage [V]")
plt.show()

plt.plot(
    processed_variables["Discharge capacity [A.h]"](t) * 48,
    processed_variables["Terminal voltage [V]"](t),
)
plt.xlabel("Discharge capacity [A.h] (48 layers)")
plt.ylabel("Terminal voltage [V]")
plt.show()

plt.plot(
    processed_variables["Discharge capacity [A.h]"](t) / (L_y * L_z),
    processed_variables["Terminal voltage [V]"](t),
)
plt.xlabel("Discharge capacity [A.h.m-2]")
plt.ylabel("Terminal voltage [V]")
plt.show()

plt.plot(
    processed_variables["Time [h]"](t),
    processed_variables["Volume-averaged cell temperature [K]"](t) - 273.15,
)
plt.xlabel("Time [h]")
plt.ylabel("Volume-averaged cell temperature [C]")
plt.show()

plt.plot(
    processed_variables["Time [h]"](t),
    processed_variables["Volume-averaged total heating [W.m-3]"](t),
)
plt.xlabel("Time [h]")
plt.ylabel("Volume-averaged total heating [W.m-3]")
plt.show()

plt.plot(
    processed_variables["Time [h]"](t),
    processed_variables["Volume-averaged total heating [W.m-3]"](t) * cell_volume,
)
plt.xlabel("Time [h]")
plt.ylabel("Total heat generation [W]")
plt.show()

#  current collector current density
times = [t[0], t[-1] / 3, t[-1] / 2, 2 * t[-1] / 3, t[-1]]
fig, axes = plt.subplots(1, len(times))
for i, time in enumerate(times):

    im = axes[i].pcolormesh(
        y,
        z,
        processed_variables["Current collector current density [A.m-2]"](
            time, y=y, z=z
        ).transpose(),
        shading="gouraud",
        cmap="plasma",
    )

    current_time = processed_variables["Time [h]"](time)
    rounded_time = round(float(current_time), 2)
    axes[i].set_xlabel(r"$y$")
    axes[i].set_ylabel(r"$z$")
    axes[i].set_title(str(rounded_time) + " hours")

    plt.colorbar(
        im,
        ax=axes[i],
        # format=ticker.FuncFormatter(fmt),
        orientation="horizontal",
        # pad=0.2,
        # format=sfmt,
    )

plt.show()

# plot negative particle surface concentation
fig, axes = plt.subplots(1, len(times))
for i, time in enumerate(times):

    im = axes[i].pcolormesh(
        y,
        z,
        processed_variables["X-averaged negative particle surface concentration"](
            time, y=y, z=z
        ).transpose(),
        shading="gouraud",
        cmap="plasma",
    )

    current_time = processed_variables["Time [h]"](time)
    rounded_time = round(float(current_time), 2)
    axes[i].set_xlabel(r"$y$")
    axes[i].set_ylabel(r"$z$")
    axes[i].set_title(str(rounded_time) + " hours")

    plt.colorbar(
        im,
        ax=axes[i],
        # format=ticker.FuncFormatter(fmt),
        orientation="horizontal",
        # pad=0.2,
        # format=sfmt,
    )

plt.show()

# plot positive particle surface concentation
fig, axes = plt.subplots(1, len(times))
for i, time in enumerate(times):

    im = axes[i].pcolormesh(
        y,
        z,
        processed_variables["X-averaged positive particle surface concentration"](
            time, y=y, z=z
        ).transpose(),
        shading="gouraud",
        cmap="plasma",
    )

    current_time = processed_variables["Time [h]"](time)
    rounded_time = round(float(current_time), 2)
    axes[i].set_xlabel(r"$y$")
    axes[i].set_ylabel(r"$z$")
    axes[i].set_title(str(rounded_time) + " hours")

    plt.colorbar(
        im,
        ax=axes[i],
        # format=ticker.FuncFormatter(fmt),
        orientation="horizontal",
        # pad=0.2,
        # format=sfmt,
    )

plt.show()

# plot cell temperature
fig, axes = plt.subplots(1, len(times))
for i, time in enumerate(times):

    im = axes[i].pcolormesh(
        y,
        z,
        processed_variables["X-averaged cell temperature [K]"](
            time, y=y, z=z
        ).transpose()
        - 273.15,
        shading="gouraud",
        cmap="plasma",
    )

    current_time = processed_variables["Time [h]"](time)
    rounded_time = round(float(current_time), 2)
    axes[i].set_xlabel(r"$y$")
    axes[i].set_ylabel(r"$z$")
    axes[i].set_title(str(rounded_time) + " hours")

    plt.colorbar(
        im,
        ax=axes[i],
        # format=ticker.FuncFormatter(fmt),
        orientation="horizontal",
        # pad=0.2,
        # format=sfmt,
    )

plt.show()
