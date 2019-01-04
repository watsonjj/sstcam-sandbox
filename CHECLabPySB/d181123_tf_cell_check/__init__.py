from CHECLabPySB import get_data, get_plot, HDF5Reader
from abc import abstractmethod, ABCMeta
import os
from CHECLabPy.utils.files import open_runlist_dl1, open_runlist_r1
import numpy as np
from target_calib import GetCellIDTCArray


class File(metaclass=ABCMeta):
    def __init__(self, **kwargs):
        self.poi = 888
        self.dead = []
        self.runlist_path = None


class Lab(File):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dead = [677, 293, 27, 1925, 1955]


class LabSM(Lab):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.poi = 30
        self.illumination_profile_path = None
        self.dead = []


class d181010_LabSM_0MHz_100mV(LabSM):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.r0_path = "/Volumes/gct-jason/data_checs/d181010_dynrange_sm/0MHz/100mV/r0/Run00980_r0.tio"
        self.ped_path = "/Volumes/gct-jason/data_checs/d181010_dynrange_sm/0MHz/100mV/r0/ped.tcal"


class TF:
    pass


class TF_Storage(TF):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.n_cell = 4096
        self.path = get_data("d181123_tf_cell_check/tf_storage/tf.tcal")
        self.plot_path = get_plot("d181123_tf_cell_check/tf_storage/tf.pdf")
        self.r1_dir = get_data("d181123_tf_cell_check/tf_storage/r1")

    def get_cell(self, fci, isample):
        return GetCellIDTCArray(fci, isample)


class TF_Sampling(TF):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.n_cell = 64
        self.path = get_data("d181123_tf_cell_check/tf_sampling/tf.tcal")
        self.plot_path = get_plot("d181123_tf_cell_check/tf_sampling/tf.pdf")
        self.r1_dir = get_data("d181123_tf_cell_check/tf_sampling/r1")

    def get_cell(self, fci, isample):
        return (fci + isample) % self.n_cell


all_files = [
    d181010_LabSM_0MHz_100mV(),
]