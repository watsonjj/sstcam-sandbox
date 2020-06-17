from glob import glob
import re
import os
from . import TF_File
from .pedestal import Pedestal_10deg, Pedestal_15deg, Pedestal_23deg, \
    Pedestal_30deg, Pedestal_40deg
from sstcam_sandbox import get_data


class DC_TF_File(TF_File):
    def __init__(self):
        super().__init__()
        self.r0_paths = None

    @property
    def reduce_cell_info_path(self):

        return get_data("d181203_erlangen/reduce_cell_info")


class DC_TF_ExtSync_File(DC_TF_File):
    @property
    def amplitudes(self):
        pattern = '(.+)/Vped_external_(.+)*_r0.tio'
        return [int(re.search(pattern, fp).group(2)) for fp in self.r0_paths]


class DC_TF_ExtSync_23deg(DC_TF_ExtSync_File):
    def __init__(self):
        super().__init__()
        self.r0_paths = glob("/Volumes/gct-jason/data_checs/d181203_erlangen/SN0038/dc_tf/externalsync/23deg/*_r0.tio")
        self.pedestal = Pedestal_23deg()


class DC_TF_ExtSync_40deg(DC_TF_ExtSync_File):
    def __init__(self):
        super().__init__()
        self.r0_paths = glob("/Volumes/gct-jason/data_checs/d181203_erlangen/SN0038/dc_tf/externalsync/40deg/*_r0.tio")
        self.pedestal = Pedestal_40deg()


class DC_TF_HardSync_File(DC_TF_File):
    @property
    def amplitudes(self):
        pattern = '(.+)/Vped_hardsync_(.+)*_r0.tio'
        return [int(re.search(pattern, fp).group(2)) for fp in self.r0_paths]


class DC_TF_HardSync_10deg(DC_TF_HardSync_File):
    def __init__(self):
        super().__init__()
        self.r0_paths = glob("/Volumes/gct-jason/data_checs/d181203_erlangen/SN0038/dc_tf/hardsync/10deg/*_r0.tio")
        self.pedestal = Pedestal_10deg()


class DC_TF_HardSync_15deg(DC_TF_HardSync_File):
    def __init__(self):
        super().__init__()
        self.r0_paths = glob("/Volumes/gct-jason/data_checs/d181203_erlangen/SN0038/dc_tf/hardsync/15deg/*_r0.tio")
        self.pedestal = Pedestal_15deg()


class DC_TF_HardSync_23deg(DC_TF_HardSync_File):
    def __init__(self):
        super().__init__()
        self.r0_paths = glob("/Volumes/gct-jason/data_checs/d181203_erlangen/SN0038/dc_tf/hardsync/23deg/*_r0.tio")
        self.pedestal = Pedestal_23deg()


class DC_TF_HardSync_30deg(DC_TF_HardSync_File):
    def __init__(self):
        super().__init__()
        self.r0_paths = glob("/Volumes/gct-jason/data_checs/d181203_erlangen/SN0038/dc_tf/hardsync/30deg/*_r0.tio")
        self.pedestal = Pedestal_30deg()


class DC_TF_HardSync_40deg(DC_TF_HardSync_File):
    def __init__(self):
        super().__init__()
        self.r0_paths = glob("/Volumes/gct-jason/data_checs/d181203_erlangen/SN0038/dc_tf/hardsync/40deg/*_r0.tio")
        self.pedestal = Pedestal_40deg()
