from pybamm import exp, constants, mechanical_parameters


def lico2_diffusivity_Dualfoil1998(sto, T):
    """
    LiCo2 diffusivity as a function of stochiometry, in this case the
    diffusivity is taken to be a constant. The value is taken from Dualfoil [1].

    References
    ----------
    .. [1] http://www.cchem.berkeley.edu/jsngrp/fortran.html

    Parameters
    ----------
    sto: :class:`pybamm.Symbol`
        Electrode stochiometry
    T: :class:`pybamm.Symbol`
        Dimensional temperature, [K]

    Returns
    -------
    :class:`pybamm.Symbol`
        Solid diffusivity
    """
    D_ref = 5.387 * 10 ** (-15)
    E_D_s = 5000
    T_ref = mechanical_parameters.T_ref
    theta_p = mechanical_parameters.theta_p
    D_ref *= 1 + theta_p * sto / T * T_ref
    arrhenius = exp(E_D_s / constants.R * (1 / T_ref - 1 / T))

    return D_ref * arrhenius
