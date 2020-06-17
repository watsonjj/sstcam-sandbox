from sstcam_sandbox import get_checs
from glob import glob
import re
from CHECLabPy.core.io import TIOReader
from CHECLabPy.utils.files import sort_file_list
import os


class File:
    def __init__(self):
        super().__init__()
        self.directory = None

    @property
    def tio_paths(self):
        return sort_file_list(glob(os.path.join(self.directory, "Run*_r1.tio")))

    @property
    def tio_readers(self):
        return [TIOReader(path) for path in self.tio_paths]

    @property
    def trigger_path(self):
        return os.path.join(self.directory, "trigger.dat")

    @property
    def monitor_paths(self):
        return [path.replace("_r1.tio", ".mon") for path in self.tio_paths]


class d190111(File):
    def __init__(self):
        super().__init__()
        self.directory = get_checs("d190111_trigger_stability/d190111")
        self.spoi = [
            151,
            101,
            399,
            # 296,
            145,
        ]


class d190118(File):
    def __init__(self):
        super().__init__()
        self.directory = get_checs("d190118_trigger_stability")
        self.spoi = [
            17,
            # 296,
            297,
            # 298,
            372,
            408,
            412,
            415,
            503
        ]

class d190121(File):
    def __init__(self):
        super().__init__()
        self.directory = get_checs("d190121_trigger_stability")
        self.spoi = [
            17,
            # 296,
            297,
            # 298,
            372,
            408,
            412,
            415,
            503
        ]
