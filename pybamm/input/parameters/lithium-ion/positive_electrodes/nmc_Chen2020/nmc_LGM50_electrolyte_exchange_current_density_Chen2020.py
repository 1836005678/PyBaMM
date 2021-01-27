from pybamm import exp, constants, Parameter, Scalar


def nmc_LGM50_electrolyte_exchange_current_density_Chen2020(c_e, c_s_surf, T):
    """
    Exchange-current density for Butler-Volmer reactions between NMC and LiPF6 in
    EC:DMC.

    References
    ----------
    .. [1] Chang-Hui Chen, Ferran Brosa Planella, Kieran O’Regan, Dominika Gastol, W.
    Dhammika Widanage, and Emma Kendrick. "Development of Experimental Techniques for
    Parameterization of Multi-scale Lithium-ion Battery Models." Journal of the
    Electrochemical Society 167 (2020): 080534.

    Parameters
    ----------
    c_e : :class:`pybamm.Symbol`
        Electrolyte concentration [mol.m-3]
    c_s_surf : :class:`pybamm.Symbol`
        Particle concentration [mol.m-3]
    T : :class:`pybamm.Symbol`
        Temperature [K]

    Returns
    -------
    :class:`pybamm.Symbol`
        Exchange-current density [A.m-2]
    """
    m_ref = Scalar(
        3.42e-6, {"A": 1, "m": 2.5, "mol": -1.5}
    )  # (A/m2)(m3/mol)**1.5 - includes ref concentrations
    E_r = Scalar(17800, "[J.mol-1]")
    arrhenius = exp(E_r / constants.R * (1 / Scalar(298.15, "[K]") - 1 / T))

    c_p_max = Parameter("Maximum concentration in positive electrode [mol.m-3]")

    return (
        m_ref * arrhenius * c_e ** 0.5 * c_s_surf ** 0.5 * (c_p_max - c_s_surf) ** 0.5
    )
