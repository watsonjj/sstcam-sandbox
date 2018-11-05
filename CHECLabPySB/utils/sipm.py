from CHECLabPySB import get_data
import numpy as np


class PE2Photons:
    def __init__(self):
        self.pde_x, self.pde_y = np.loadtxt(get_data('charge_resolution/pe_to_photons/PDE.csv'), unpack=True, delimiter=', ')
        self.crosstalk_x, self.crosstalk_y = np.loadtxt(get_data('charge_resolution/pe_to_photons/crosstalk.csv'), unpack=True, delimiter=', ')

    def convert(self, opct):
        opct_y = self.crosstalk_y / 100
        pde_y = self.pde_y / 100

        if (opct > opct_y.max()) | (opct < opct_y.min()):
            return np.nan
            # raise ValueError("Value of crosstalk out of range")

        vover = np.interp(opct, opct_y, self.crosstalk_x)

        if (vover > self.pde_x.max()) | (vover < self.pde_x.min()):
            return np.nan
            # raise ValueError("Value of vover out of range")

        pde = np.interp(vover, self.pde_x, pde_y)

        return 1/pde
