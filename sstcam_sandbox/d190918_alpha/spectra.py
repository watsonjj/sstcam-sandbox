import numpy as np
from astropy import units as u


@u.quantity_input
def norm_crab(e_min: u.TeV, e_max: u.TeV,
              area: u.m**2, solid_angle: u.deg, mc_index, energies: u.TeV, n_simulated):
    norm = 2.83e-14 / (u.GeV * u.cm**2 * u.s)
    index = -2.62

    weights = energies.to_value(u.TeV) ** (index - mc_index)

    a = e_min.to_value('TeV')
    b = e_max.to_value('TeV')
    norm_ = norm.to(1 / (u.TeV * u.s * u.m**2)) * u.TeV
    integral = norm_ * (b**(mc_index + 1) - a**(mc_index + 1)) / (mc_index + 1)
    t_norm = (n_simulated / (integral * area)).to_value(u.s)

    return weights, t_norm


@u.quantity_input
def norm_proton(e_min: u.TeV, e_max: u.TeV,
                area: u.m**2, solid_angle: u.deg, mc_index, energies: u.TeV, n_simulated):
    norm = 9.6e-9 / (u.GeV * u.cm ** 2 * u.s * u.sr)
    index = -2.7

    weights = energies.to_value(u.TeV) ** (index - mc_index)

    a = e_min.to_value('TeV')
    b = e_max.to_value('TeV')
    norm_ = norm.to(1 / (u.TeV * u.s * u.m**2 * u.sr)) * u.TeV
    angle = ((1 - np.cos(solid_angle.to_value('rad')))*2*np.pi*u.sr)
    integral = norm_ * (b**(mc_index + 1) - a**(mc_index + 1)) / (mc_index + 1)
    t_norm = (n_simulated / (integral * area * angle)).to_value(u.s)

    return weights, t_norm
