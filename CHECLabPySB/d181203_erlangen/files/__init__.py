from .. import poi
import os


class File:
    def __init__(self):
        self.poi = poi


class TF_File(File):
    def __init__(self):
        super().__init__()
        self.r0_paths = None

    @property
    def tf_path(self):
        directory = os.path.dirname(self.r0_paths[0])
        return os.path.join(directory, "tf.tcal")


def child_subclasses(base):
    family = base.__subclasses__() + [
        g for s in base.__subclasses__()
        for g in child_subclasses(s)
    ]
    children = [g for g in family if not g.__subclasses__()]
    return children


"""
class DynRange_aaa(DynRange_File):
    def __init__(self):
        super().__init__()
        self.r0_paths = glob("/Volumes/gct-jason/data_checs/d181203_erlangen/SN0038/dynrange/aaa/r0/Amplitude_*_Run_0.tio")
        self.pedestal = Pedestal_aaa()


class DynRange_aaa_TFNone(DynRange_aaa):
    def __init__(self):
        super().__init__()
        self.subdir = "tf_none"
        self.tf = None


class DynRange_aaa_TFAC23(DynRange_aaa):
    def __init__(self):
        super().__init__()
        self.subdir = "tf_ac23"
        self.tf = AC_TF_23deg()


class DynRange_aaa_TFAC40(DynRange_aaa):
    def __init__(self):
        super().__init__()
        self.subdir = "tf_ac40"
        self.tf = AC_TF_40deg()


class DynRange_aaa_TFDC10(DynRange_aaa):
    def __init__(self):
        super().__init__()
        self.subdir = "tf_dc10"
        self.tf = DC_TF_HardSync_10deg()


class DynRange_aaa_TFDC23(DynRange_aaa):
    def __init__(self):
        super().__init__()
        self.subdir = "tf_dc23"
        self.tf = DC_TF_HardSync_23deg()


class DynRange_aaa_TFDC30(DynRange_aaa):
    def __init__(self):
        super().__init__()
        self.subdir = "tf_dc30"
        self.tf = DC_TF_HardSync_30deg()


class DynRange_aaa_TFDC40(DynRange_aaa):
    def __init__(self):
        super().__init__()
        self.subdir = "tf_dc40"
        self.tf = DC_TF_HardSync_40deg()
"""