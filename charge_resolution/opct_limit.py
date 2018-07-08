import numpy as np
from scipy.special import binom
from numba import jit
from scipy.stats import poisson, norm as gaus
from scipy.special import factorial
from matplotlib import pyplot as plt
from IPython import embed
from CHECLabPy.utils.resolutions import ChargeResolution, ChargeStatistics
import pandas as pd
import os
from tqdm import tqdm


C = np.sqrt(2.0 * np.pi)
NPEAKS = 1000

N = np.arange(NPEAKS)[:, None]
J = np.arange(NPEAKS)[None, :]
K = np.arange(1, NPEAKS)[:, None]
FACTORIAL_INV = 1 / factorial(np.arange(NPEAKS))[None, :]
BINOM = binom(N - 1, J - 1)

x = np.arange(NPEAKS)
def get_distribution(opct, lambda_):
    pj = poisson.pmf(J, lambda_)
    pct = np.nansum(pj * np.power(1 - opct, J) * np.power(opct, N - J) * BINOM, 1)
    pct[0] = poisson.pmf(0, lambda_)
    return pct


# norm = 1
# eped = 0
# eped_sigma = 5.05
# spe = 16.859
# spe_sigma = 1.81
# spe_sigma /= spe
# eped_sigma /= spe
# spe /= spe
# x = np.linspace(-1.5, 500, 10000)
# def get_distribution(opct, lambda_):
#     p_ped = poisson.pmf(0, lambda_)
#     ped_signal = norm * p_ped * gaus.pdf(x, eped, eped_sigma)
#
#     pj = poisson.pmf(J, lambda_)
#     pct = np.nansum(pj * np.power(1-opct, J) * np.power(opct, N - J) * BINOM, 1)
#
#     sap = spe_sigma
#
#     pe_sigma = np.sqrt(K * spe_sigma ** 2 + eped_sigma ** 2)
#
#     signal = pct[K] * gaus.pdf(x, eped + K * spe, pe_sigma)
#     signal *= norm
#     pe_signal = np.nansum(signal, 0)
#
#     s = ped_signal + pe_signal
#     s /= s.sum()
#
#     return s

opct = 0.38
lambda_ = 1

cr = ChargeResolution()
cs = ChargeStatistics()
desc = "Looping over lambdas"
true_arr = np.geomspace(0.1, 400, 100)
for lambda_ in tqdm(true_arr, desc=desc):
    pixel = 1920
    dist = get_distribution(opct, lambda_)
    n = 100000
    measured = np.random.choice(x, p=dist, size=n)
    true = lambda_
    cr.add(pixel, true, measured)
    cs.add(pixel, true, measured)
df_pixel, _ = cr.finish()
x = df_pixel['true']
cr = df_pixel['rmse']
df_pixel, _ = cs.finish()
mean = df_pixel['mean']

np.savez("opct_limit.npz", x=x, cr=cr, mean=mean)
