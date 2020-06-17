from glob import glob
import re
from CHECLabPy.core.io import TIOReader
import os


class File:
    def __init__(self):
        super().__init__()
        self.directory = None

    @property
    def tio_paths(self):
        return glob(os.path.join(self.directory, "Run*_r1.tio"))

    @property
    def tio_readers(self):
        return [TIOReader(path) for path in self.tio_paths]

    @property
    def trigger_path(self):
        return os.path.join(self.directory, "trigger.dat")

    @property
    def monitor_paths(self):
        return glob(os.path.join(self.directory, "Run*.mon"))


class d190111(File):
    def __init__(self):
        super().__init__()
        self.directory = "/Volumes/gct-jason/data_checs/d190111_trigger_stability/d190111"
        self.spoi = {
            151: 'Fast Dropoff',
            101: 'Normal',
            399: 'Dead',
            # 296: 'High',
            145: 'Slow Dropoff',
        }


class d190115_1mAcut(File):
    def __init__(self):
        super().__init__()
        self.directory = "/Volumes/gct-jason/data_checs/d190111_trigger_stability/d190115_1mAcut"
        self.spoi = {
            151: 'Fast Dropoff',
            101: 'Normal',
            399: 'Dead',
            # 296: 'High',
            145: 'Slow Dropoff',
        }
        self.hv_path = "/Volumes/gct-jason/data_checs/d190111_trigger_stability/hvSetting_no_above_1mA.cfg"


class d190115_1mAcut_12h(File):
    def __init__(self):
        super().__init__()
        self.directory = "/Volumes/gct-jason/data_checs/d190111_trigger_stability/d190115_1mAcut_12h"
        self.spoi = {
            151: 'Fast Dropoff',
            101: 'Normal',
            399: 'Dead',
            # 296: 'High',
            145: 'Slow Dropoff',
        }
        self.hv_path = "/Volumes/gct-jason/data_checs/d190111_trigger_stability/hvSetting_no_above_1mA.cfg"
