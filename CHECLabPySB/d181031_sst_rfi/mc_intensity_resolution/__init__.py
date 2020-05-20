from CHECLabPySB import get_data, get_plot
from CHECLabPySB.old.io import HDF5Reader
from abc import abstractmethod, ABCMeta
import os
from CHECLabPy.utils.files import open_runlist_dl1, open_runlist_r1
import numpy as np
from glob import glob


class File(metaclass=ABCMeta):
    def __init__(self, **kwargs):
        self.poi = 238
        self.dead = []
        self.dl1_paths = None
        self.pde = None

    @property
    def mc_calib_path(self):
        return get_data("d181031_sst_rfi/mc_intensity_resolution/mc_calibration/{}.h5".format(self.__class__.__name__))

    @property
    def intensity_resolution_path(self):
        return get_data("d181031_sst_rfi/mc_intensity_resolution/{}.h5".format(self.__class__.__name__))


class MCOnsky(File):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dead = []


class d181030_MCOnsky_Prod3(MCOnsky):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dl1_paths = glob("/Volumes/gct-jason/sim_telarray/d181030_onsky/prod3/*_dl1.h5")
        self.pde = 0.345


class d181030_MCOnsky_Prod4(MCOnsky):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dl1_paths = glob("/Volumes/gct-jason/sim_telarray/d181030_onsky/prod4/*_dl1.h5")
        self.pde = 0.39


calib_files = [
    d181030_MCOnsky_Prod3(),
    d181030_MCOnsky_Prod4(),
]


all_files = [
    d181030_MCOnsky_Prod3(),
    d181030_MCOnsky_Prod4(),
]
