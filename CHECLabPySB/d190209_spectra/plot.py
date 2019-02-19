import numpy as np
from math import factorial
from scipy.special import binom
from scipy.stats import norm as gaus, poisson
from scipy.signal import unit_impulse
from numba import jit
from CHECLabPy.core.spectrum_fitter import SpectrumFitter
from matplotlib import pyplot as plt
from IPython import embed


C = np.sqrt(2.0 * np.pi)
FACTORIAL = np.array([factorial(i) for i in range(15)])
FACTORIAL_0 = FACTORIAL[0]
NPEAKS = 11
N = np.arange(NPEAKS)[:, None]
J = np.arange(NPEAKS)[None, :]
K = np.arange(1, NPEAKS)[:, None]
FACTORIAL_J_INV = 1 / FACTORIAL[J]
BINOM = binom(N - 1, J - 1)

# def _normal_pdf(x, mean=0, std_deviation=1):
#     u = (x - mean) / std_deviation
#     return np.exp(-0.5 * u ** 2) / (C * std_deviation)


def _poisson_pmf_j(mu):
    return mu ** J * np.exp(-mu) * FACTORIAL_J_INV


def pedestal_signal(x, norm, eped, eped_sigma, lambda_):
    p_ped = np.exp(-lambda_)  # Poisson PMF for k = 0, mu = lambda_
    signal = norm * p_ped * gaus.pdf(x, eped, eped_sigma)
    return signal


def pe_signal(k, x, norm, eped, eped_sigma, spe, spe_sigma, lambda_):
    p = _poisson_pmf_j(lambda_)[0]
    pe_sigma = np.sqrt(k * spe_sigma ** 2 + eped_sigma ** 2)
    signal = norm * p[k] * gaus.pdf(x, eped + k * spe, pe_sigma)
    return signal


def mapm(x, norm, eped, eped_sigma, spe, spe_sigma, lambda_):
    params = [norm, eped, eped_sigma, lambda_]
    ped_s = pedestal_signal(x, *params)
    params = [norm, eped, eped_sigma, spe, spe_sigma, lambda_]
    pe_s = pe_signal(K, x[None, :], *params).sum(0)
    signal = ped_s + pe_s
    return signal


def main():
    kwargs = dict(
        norm=1,
        eped=0,
        eped_sigma=0.1,
        spe=1,
        spe_sigma=0.1,
        lambda_=2,
    )

    x = np.linspace(-1, 10, 100000)
    y = mapm(x, **kwargs)
    print(np.average(x, weights=y))

    plt.plot(x, y)
    plt.show()

if __name__ == '__main__':
    main()
