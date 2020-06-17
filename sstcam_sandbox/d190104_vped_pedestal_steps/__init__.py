from glob import glob
import re
from CHECLabPy.core.io import TIOReader


class File:
    def __init__(self):
        super().__init__()
        self.r0_paths = None

    @property
    def r0_readers(self):
        return [TIOReader(path) for path in self.r0_paths]


class DC_TF_ExtSync_File(File):
    @property
    def amplitudes(self):
        pattern = '(.+)/Vped_external_(.+)*_r0.tio'
        return [int(re.search(pattern, fp).group(2)) for fp in self.r0_paths]


class DC_TF_ExtSync_23deg(DC_TF_ExtSync_File):
    def __init__(self):
        super().__init__()
        self.r0_paths = glob("/Volumes/gct-jason/data_checs/d181203_erlangen/SN0038/dc_tf/externalsync/23deg/*_r0.tio")
