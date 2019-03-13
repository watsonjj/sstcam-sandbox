import numpy as np
from numba import jit, prange
from math import lgamma, exp, pow, sqrt, log


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
def mapm(x, norm, eped, eped_sigma, spe, spe_sigma, lambda_):
    # Obtain pedestal peak
    p_ped = exp(-lambda_)
    ped_signal = norm * p_ped * normal_pdf(x, eped, eped_sigma)

    pe_signal = 0
    found = False

    # Loop over the possible total number of cells fired
    for k in prange(1, 250):
        p = poisson(k, lambda_)  # Probability to get k avalanches

        # Skip insignificant probabilities
        if (not found) & (p < 1e-5):
            continue
        if found & (p < 1e-5):
            break
        found = True

        # Combine spread of pedestal and pe peaks
        pe_sigma = sqrt(k * spe_sigma ** 2 + eped_sigma ** 2)

        # Evaluate probability at each value of x
        pe_signal += norm * p * normal_pdf(x, eped + k * spe, pe_sigma)

    return ped_signal + pe_signal


@jit(fastmath=True, parallel=True)
def sipm(x, norm, eped, eped_sigma, spe, spe_sigma, lambda_, opct, pap, dap):
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
