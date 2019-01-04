from glob import glob
import re
from . import TF_File
from .pedestal import Pedestal_23deg_AC, Pedestal_40deg_AC


class AC_TF_File(TF_File):
    def __init__(self):
        super().__init__()
        self.r0_paths = None

    @property
    def amplitudes(self):
        pattern = '(.+)/Amplitude_(.+)*_r0.tio'
        return [int(re.search(pattern, fp).group(2)) for fp in self.r0_paths]


class AC_TF_23deg(AC_TF_File):
    def __init__(self):
        super().__init__()
        self.r0_paths = glob("/Volumes/gct-jason/data_checs/d181203_erlangen/SN0038/ac_tf/23deg/*_r0.tio")
        self.pedestal = Pedestal_23deg_AC()


class AC_TF_40deg(AC_TF_File):
    def __init__(self):
        super().__init__()
        self.r0_paths = glob("/Volumes/gct-jason/data_checs/d181203_erlangen/SN0038/ac_tf/40deg/*_r0.tio")
        self.pedestal = Pedestal_40deg_AC()
