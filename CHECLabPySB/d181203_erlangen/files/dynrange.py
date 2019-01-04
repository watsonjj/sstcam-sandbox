from glob import glob
import re
from .dc_tf import *
from .ac_tf import *
from . import child_subclasses
from . import File


class DynRange_File(File):
    def __init__(self):
        super().__init__()
        self.r0_paths = None
        self.subdir = None

    @property
    def r1_paths(self):
        return [p.replace("/r0/", "/{}/".format(self.subdir))
                for p in self.r0_paths]

    @property
    def amplitudes(self):
        pattern = '(.+)/Amplitude_(.+)*_Run_(.+)_r0.tio'
        return [int(re.search(pattern, fp).group(2)) for fp in self.r0_paths]
        

class DynRange_10deg(DynRange_File):
    def __init__(self):
        super().__init__()
        self.r0_paths = glob("/Volumes/gct-jason/data_checs/d181203_erlangen/SN0038/dynrange/10deg/r0/Amplitude_*_Run_0.tio")
        self.pedestal = Pedestal_10deg()


class DynRange_10deg_TFNone(DynRange_10deg):
    def __init__(self):
        super().__init__()
        self.subdir = "tf_none"
        self.tf = None


class DynRange_10deg_TFAC23(DynRange_10deg):
    def __init__(self):
        super().__init__()
        self.subdir = "tf_ac23"
        self.tf = AC_TF_23deg()


class DynRange_10deg_TFAC40(DynRange_10deg):
    def __init__(self):
        super().__init__()
        self.subdir = "tf_ac40"
        self.tf = AC_TF_40deg()


class DynRange_10deg_TFDC10(DynRange_10deg):
    def __init__(self):
        super().__init__()
        self.subdir = "tf_dc10"
        self.tf = DC_TF_HardSync_10deg()


class DynRange_10deg_TFDC23(DynRange_10deg):
    def __init__(self):
        super().__init__()
        self.subdir = "tf_dc23"
        self.tf = DC_TF_HardSync_23deg()


class DynRange_10deg_TFDC30(DynRange_10deg):
    def __init__(self):
        super().__init__()
        self.subdir = "tf_dc30"
        self.tf = DC_TF_HardSync_30deg()


class DynRange_10deg_TFDC40(DynRange_10deg):
    def __init__(self):
        super().__init__()
        self.subdir = "tf_dc40"
        self.tf = DC_TF_HardSync_40deg()


class DynRange_15deg(DynRange_File):
    def __init__(self):
        super().__init__()
        self.r0_paths = glob("/Volumes/gct-jason/data_checs/d181203_erlangen/SN0038/dynrange/15deg/r0/Amplitude_*_Run_0.tio")
        self.pedestal = Pedestal_15deg()


class DynRange_15deg_TFNone(DynRange_15deg):
    def __init__(self):
        super().__init__()
        self.subdir = "tf_none"
        self.tf = None


class DynRange_15deg_TFAC23(DynRange_15deg):
    def __init__(self):
        super().__init__()
        self.subdir = "tf_ac23"
        self.tf = AC_TF_23deg()


class DynRange_15deg_TFAC40(DynRange_15deg):
    def __init__(self):
        super().__init__()
        self.subdir = "tf_ac40"
        self.tf = AC_TF_40deg()


class DynRange_15deg_TFDC10(DynRange_15deg):
    def __init__(self):
        super().__init__()
        self.subdir = "tf_dc10"
        self.tf = DC_TF_HardSync_10deg()


class DynRange_15deg_TFDC23(DynRange_15deg):
    def __init__(self):
        super().__init__()
        self.subdir = "tf_dc23"
        self.tf = DC_TF_HardSync_23deg()


class DynRange_15deg_TFDC30(DynRange_15deg):
    def __init__(self):
        super().__init__()
        self.subdir = "tf_dc30"
        self.tf = DC_TF_HardSync_30deg()


class DynRange_15deg_TFDC40(DynRange_15deg):
    def __init__(self):
        super().__init__()
        self.subdir = "tf_dc40"
        self.tf = DC_TF_HardSync_40deg()
        

class DynRange_23deg(DynRange_File):
    def __init__(self):
        super().__init__()
        self.r0_paths = glob("/Volumes/gct-jason/data_checs/d181203_erlangen/SN0038/dynrange/23deg/r0/Amplitude_*_Run_0.tio")
        self.pedestal = Pedestal_23deg()


class DynRange_23deg_TFNone(DynRange_23deg):
    def __init__(self):
        super().__init__()
        self.subdir = "tf_none"
        self.tf = None


class DynRange_23deg_TFAC23(DynRange_23deg):
    def __init__(self):
        super().__init__()
        self.subdir = "tf_ac23"
        self.tf = AC_TF_23deg()


class DynRange_23deg_TFAC40(DynRange_23deg):
    def __init__(self):
        super().__init__()
        self.subdir = "tf_ac40"
        self.tf = AC_TF_40deg()


class DynRange_23deg_TFDC10(DynRange_23deg):
    def __init__(self):
        super().__init__()
        self.subdir = "tf_dc10"
        self.tf = DC_TF_HardSync_10deg()


class DynRange_23deg_TFDC23(DynRange_23deg):
    def __init__(self):
        super().__init__()
        self.subdir = "tf_dc23"
        self.tf = DC_TF_HardSync_23deg()


class DynRange_23deg_TFDC30(DynRange_23deg):
    def __init__(self):
        super().__init__()
        self.subdir = "tf_dc30"
        self.tf = DC_TF_HardSync_30deg()


class DynRange_23deg_TFDC40(DynRange_23deg):
    def __init__(self):
        super().__init__()
        self.subdir = "tf_dc40"
        self.tf = DC_TF_HardSync_40deg()
        

class DynRange_30deg(DynRange_File):
    def __init__(self):
        super().__init__()
        self.r0_paths = glob("/Volumes/gct-jason/data_checs/d181203_erlangen/SN0038/dynrange/30deg/r0/Amplitude_*_Run_0.tio")
        self.pedestal = Pedestal_30deg()


class DynRange_30deg_TFNone(DynRange_30deg):
    def __init__(self):
        super().__init__()
        self.subdir = "tf_none"
        self.tf = None


class DynRange_30deg_TFAC23(DynRange_30deg):
    def __init__(self):
        super().__init__()
        self.subdir = "tf_ac23"
        self.tf = AC_TF_23deg()


class DynRange_30deg_TFAC40(DynRange_30deg):
    def __init__(self):
        super().__init__()
        self.subdir = "tf_ac40"
        self.tf = AC_TF_40deg()


class DynRange_30deg_TFDC10(DynRange_30deg):
    def __init__(self):
        super().__init__()
        self.subdir = "tf_dc10"
        self.tf = DC_TF_HardSync_10deg()


class DynRange_30deg_TFDC23(DynRange_30deg):
    def __init__(self):
        super().__init__()
        self.subdir = "tf_dc23"
        self.tf = DC_TF_HardSync_23deg()


class DynRange_30deg_TFDC30(DynRange_30deg):
    def __init__(self):
        super().__init__()
        self.subdir = "tf_dc30"
        self.tf = DC_TF_HardSync_30deg()


class DynRange_30deg_TFDC40(DynRange_30deg):
    def __init__(self):
        super().__init__()
        self.subdir = "tf_dc40"
        self.tf = DC_TF_HardSync_40deg()


class DynRange_40deg(DynRange_File):
    def __init__(self):
        super().__init__()
        self.r0_paths = glob("/Volumes/gct-jason/data_checs/d181203_erlangen/SN0038/dynrange/40deg/r0/Amplitude_*_Run_0.tio")
        self.pedestal = Pedestal_40deg()


class DynRange_40deg_TFNone(DynRange_40deg):
    def __init__(self):
        super().__init__()
        self.subdir = "tf_none"
        self.tf = None


class DynRange_40deg_TFAC23(DynRange_40deg):
    def __init__(self):
        super().__init__()
        self.subdir = "tf_ac23"
        self.tf = AC_TF_23deg()


class DynRange_40deg_TFAC40(DynRange_40deg):
    def __init__(self):
        super().__init__()
        self.subdir = "tf_ac40"
        self.tf = AC_TF_40deg()


class DynRange_40deg_TFDC10(DynRange_40deg):
    def __init__(self):
        super().__init__()
        self.subdir = "tf_dc10"
        self.tf = DC_TF_HardSync_10deg()


class DynRange_40deg_TFDC23(DynRange_40deg):
    def __init__(self):
        super().__init__()
        self.subdir = "tf_dc23"
        self.tf = DC_TF_HardSync_23deg()


class DynRange_40deg_TFDC30(DynRange_40deg):
    def __init__(self):
        super().__init__()
        self.subdir = "tf_dc30"
        self.tf = DC_TF_HardSync_30deg()


class DynRange_40deg_TFDC40(DynRange_40deg):
    def __init__(self):
        super().__init__()
        self.subdir = "tf_dc40"
        self.tf = DC_TF_HardSync_40deg()


all_files = child_subclasses(DynRange_File)
