from CHECLabPy.core.spectrum_fitter import SpectrumFitter
from numba import jit, prange
from math import lgamma, exp, pow, sqrt, log
import numpy as np


class GentileFitterNew(SpectrumFitter):
    def __init__(self, n_illuminations, config_path=None):
        super().__init__(n_illuminations, config_path)

        self.nbins = 100
        self.range = [-40, 150]

        self.add_parameter("norm", None, 0, 100000, fix=True, multi=True)
        self.add_parameter("eped", 0, -10, 10)
        self.add_parameter("eped_sigma", 9, 2, 20)
        self.add_parameter("spe", 25, 15, 40)
        self.add_parameter("spe_sigma", 2, 1, 20)
        self.add_parameter("lambda_", 5, 0.01, 10, multi=True)
        self.add_parameter("opct", 0.4, 0.01, 0.8)
        self.add_parameter("pap", 0.09, 0.01, 0.8)
        self.add_parameter("dap", 0.5, 0, 0.8)

    def _prepare_params(self, p0, limits, fix):
        for i in range(self.n_illuminations):
            norm = 'norm{}'.format(i)
            if p0[norm] is None:
                p0[norm] = np.trapz(self.hist[i], self.between)

    @staticmethod
    def _fit(x, **kwargs):
        return sipm(x, **kwargs)


SQRT2PI = np.sqrt(2.0 * np.pi)


@jit(nopython=True, fastmath=True, parallel=True)
def binom(n, k):
    return exp(lgamma(n + 1) - lgamma(k + 1) - lgamma(n - k + 1))


@jit(nopython=True, fastmath=True, parallel=True)
def poisson(k, mu):
    return exp(k * log(mu) - mu - lgamma(k + 1))


@jit(nopython=True, fastmath=True, parallel=True)
def normal_pdf(x, mean=0, std_deviation=1):
    u = (x - mean) / std_deviation
    return np.exp(-0.5 * u ** 2) / (SQRT2PI * std_deviation)


@jit(fastmath=True, parallel=True)
def sipm_nb(x, norm, eped, eped_sigma, spe, spe_sigma, lambda_, opct, pap, dap):
    sap = spe_sigma  # Assume the sigma of afterpulses is the same

    # Obtain pedestal peak
    p_ped = exp(-lambda_)
    ped_signal = norm * p_ped * normal_pdf(x, eped, eped_sigma)

    pe_signal = np.zeros(x.size)
    found = False

    # Loop over the possible total number of cells fired
    for k in prange(1, 250):
        pk = 0
        for j in prange(1, k+1):
            pj = poisson(j, lambda_)  # Probability for j initial fired cells

            # Skip insignificant probabilities
            if pj < 1e-5:
                continue

            # Sum the probability from the possible combinations which result
            # in a total of k fired cells to get the total probability of k
            # fired cells
            pk += pj * pow(1-opct, j) * pow(opct, k-j) * binom(k-1, j-1)

        # Skip insignificant probabilities
        if (not found) & (pk < 1e-5):
            continue
        if found & (pk < 1e-5):
            break
        found = True

        # Consider probability of afterpulses
        papk = pow(1 - pap, k)
        p0ap = pk * papk
        pap1 = pk * (1-papk) * papk

        # Combine spread of pedestal and pe (and afterpulse) peaks
        pe_sigma = sqrt(k * spe_sigma ** 2 + eped_sigma ** 2)
        ap_sigma = sqrt(k * sap ** 2 + eped_sigma ** 2)

        # Evaluate probability at each value of x
        pe_signal += norm * (
                p0ap * normal_pdf(x, eped + k * spe, pe_sigma) +
                pap1 * normal_pdf(x, eped + k * spe * (1 - dap), ap_sigma)
        )

    return ped_signal + pe_signal


def sipm(x, norm, eped, eped_sigma, spe, spe_sigma, lambda_, opct, pap, dap, **kwargs):
    return sipm_nb(x,  norm, eped, eped_sigma, spe, spe_sigma, lambda_, opct, pap, dap)
