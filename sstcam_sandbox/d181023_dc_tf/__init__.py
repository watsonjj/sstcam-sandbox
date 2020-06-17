from sstcam_sandbox import get_data, get_plot, HDF5Reader
from abc import abstractmethod, ABCMeta
import os
from CHECLabPy.utils.files import open_runlist_dl1, open_runlist_r1
from CHECLabPy.utils.files import sort_file_list
import numpy as np
from glob import glob


def ordered_glob(txt):
    return sort_file_list(glob(txt))[1:]


class File(metaclass=ABCMeta):
    def __init__(self, **kwargs):
        self.base_path = None

    @property
    def r0_paths(self):
        return ordered_glob(os.path.join(self.base_path, "r0/Run*_r0.tio"))

    @property
    def vped_paths(self):
        return [f.replace("_r0.tio", "_vped.txt") for f in self.r0_paths]

    @property
    def tfnone_paths(self):
        return ordered_glob(os.path.join(self.base_path, "tf_none/Run*_r1.tio"))

    @property
    def tfpoly_paths(self):
        return ordered_glob(os.path.join(self.base_path, "tf_poly/Run*_r1.tio"))

    @property
    def vped_list(self):
        l = []
        for p in self.vped_paths:
            with open(p) as f:
                l.append(int(f.readline()))
        return l

    @property
    def averages_path(self):
        return get_data(os.path.join("d181023_df_tf/averages/", self.__class__.__name__))


class d181023_13C(File):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.base_path = "/Volumes/gct-jason/data_checs/d181023_dctf/13C/"


class d181023_23C(File):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.base_path = "/Volumes/gct-jason/data_checs/d181023_dctf/23C/"


class d181023_33C(File):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.base_path = "/Volumes/gct-jason/data_checs/d181023_dctf/33C/"


class d181023_43C(File):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.base_path = "/Volumes/gct-jason/data_checs/d181023_dctf/43C/"


all_files = [
    d181023_13C(),
    d181023_23C(),
    d181023_33C(),
    d181023_43C(),
]
