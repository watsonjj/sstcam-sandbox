import iminuit
import numpy as np
from scipy.stats import poisson
from functools import partial
from CHECLabPy.spectrum_fitters.gentile import pe_signal, K
from IPython import embed


def function(x, spe_sigma, lambda_, opct, pap, dap):
    signal = pe_signal(
        K,
        x,
        1,
        0,
        0,
        1,
        spe_sigma,
        lambda_,
        opct,
        pap,
        dap
    ).sum(0)

    trap = (x[1:] - x[:-1]) * 0.5 * (signal[1:] + signal[:-1])
    i_spe = np.sum(trap)
    i_xspe = np.sum((x[1:] + x[:-1]) * 0.5 * trap)

    norm_x = i_spe / i_xspe
    norm_spe = 1. / (i_spe * norm_x)

    y = np.interp(x, x * norm_x, signal * norm_spe)

    return y


def minimize(y, x, spe_sigma, lambda_, opct, pap, dap):
    p = function(x, spe_sigma, lambda_, opct, pap, dap)
    like = -2 * poisson._logpmf(y, p)
    return np.nansum(like)


def main():
    f = np.loadtxt("/Users/Jason/Software/CHECLabPy_sandbox/mc_config/spe_spectrum_fix/SPEspectrum_57.50_2.500_0.080.dat", unpack=True)
    x = f[0]
    spe = f[1]

    def mini(spe_sigma, lambda_, opct, pap, dap):
        return minimize(spe, x, spe_sigma, lambda_, opct, pap, dap)

    p0 = dict(
        spe_sigma=1,
        lambda_=1,
        opct=0.1,
        pap=0.1,
        dap=0.1
    )
    limits = dict(
        limit_spe_sigma=(0.01, 2),
        limit_lambda_=(0.01, 2),
        limit_opct=(0.01, 1),
        limit_pap=(0.01, 0.2),
        limit_dap=(0.01, 0.2),
    )

    m0 = iminuit.Minuit(
        mini, **p0, **limits, print_level=0, pedantic=False, throw_nan=True,
        # forced_parameters=['spe_sigma', 'lambda_', 'opct', 'pap', 'dap']
    )
    m0.migrad()

    embed()


# i_spe = 0
# i_xspe = 0
#
# for i in range(1, n):
#     i_spe += (x[i] - x[i - 1]) * 0.5 * (spe[i] + spe[i - 1])
#     i_xspe += 0.5 * (x[i] + x[i - 1]) * (x[i] - x[i - 1]) * 0.5 * (spe[i] + spe[i - 1])
#
# print(i_spe, i_xspe)
#
# i_spe = np.trapz(spe, x)
#
#
# embed()

if __name__ == '__main__':
    main()