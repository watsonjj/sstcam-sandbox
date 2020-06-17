import ctypes
import numpy as np
import os


lib = np.ctypeslib.load_library("spe_functions", os.path.dirname(__file__))
mapm_c = lib.mapm
mapm_c.restype = None
mapm_c.argtypes = [
    np.ctypeslib.ndpointer(ctypes.c_double, flags="C_CONTIGUOUS"),
    np.ctypeslib.ndpointer(ctypes.c_double, flags="C_CONTIGUOUS"),
    ctypes.c_size_t,
    ctypes.c_double,
    ctypes.c_double,
    ctypes.c_double,
    ctypes.c_double,
    ctypes.c_double,
    ctypes.c_double,
]

sipm_c = lib.sipm
sipm_c.restype = None
sipm_c.argtypes = [
    np.ctypeslib.ndpointer(ctypes.c_double, flags="C_CONTIGUOUS"),
    np.ctypeslib.ndpointer(ctypes.c_double, flags="C_CONTIGUOUS"),
    ctypes.c_size_t,
    ctypes.c_double,
    ctypes.c_double,
    ctypes.c_double,
    ctypes.c_double,
    ctypes.c_double,
    ctypes.c_double,
    ctypes.c_double,
    ctypes.c_double,
    ctypes.c_double,
]


def mapm(x, norm, eped, eped_sigma, spe, spe_sigma, lambda_, **kwargs):
    y = np.zeros(x.size, dtype=np.double)
    mapm_c(x, y, y.size, norm, eped, eped_sigma, spe, spe_sigma, lambda_)
    return y


def sipm(x, norm, eped, eped_sigma, spe, spe_sigma, lambda_, opct, pap, dap, **kwargs):
    y = np.zeros(x.size, dtype=np.double)
    sipm_c(x, y, y.size,  norm, eped, eped_sigma, spe, spe_sigma,
           lambda_, opct, pap, dap)
    return y
