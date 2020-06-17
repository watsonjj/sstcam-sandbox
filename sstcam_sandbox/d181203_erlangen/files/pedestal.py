from glob import glob
import re
import os
from subprocess import call
from . import child_subclasses, File


def generate_ped(path):
    cmd = "generate_ped -i {}".format(path)
    print("Executing: {}".format(cmd))
    call(cmd, shell=True)


class Pedestal_File(File):
    def __init__(self):
        super().__init__()
        self.r0_path = None

    @property
    def path(self):
        path = self.r0_path.replace("_r0.tio", "_ped.tcal")
        if not os.path.exists(path):
            print("No pedestal found in path: {}".format(path))
            generate_ped(self.r0_path)
            assert os.path.exists(path)
        return path


class Pedestal_10deg(Pedestal_File):
    def __init__(self):
        super().__init__()
        self.r0_path = "/Volumes/gct-jason/data_checs/d181203_erlangen/SN0038/pedestal/Pedestal_10deg_r0.tio"


class Pedestal_15deg(Pedestal_File):
    def __init__(self):
        super().__init__()
        self.r0_path = "/Volumes/gct-jason/data_checs/d181203_erlangen/SN0038/pedestal/Pedestal_15deg_r0.tio"


class Pedestal_23deg(Pedestal_File):
    def __init__(self):
        super().__init__()
        self.r0_path = "/Volumes/gct-jason/data_checs/d181203_erlangen/SN0038/pedestal/Pedestal_23deg_r0.tio"


class Pedestal_30deg(Pedestal_File):
    def __init__(self):
        super().__init__()
        self.r0_path = "/Volumes/gct-jason/data_checs/d181203_erlangen/SN0038/pedestal/Pedestal_30deg_r0.tio"


class Pedestal_40deg(Pedestal_File):
    def __init__(self):
        super().__init__()
        self.r0_path = "/Volumes/gct-jason/data_checs/d181203_erlangen/SN0038/pedestal/Pedestal_40deg_r0.tio"


class Pedestal_23deg_AC(Pedestal_File):
    def __init__(self):
        super().__init__()
        self.r0_path = "/Volumes/gct-jason/data_checs/d181203_erlangen/SN0038/ac_tf/23deg/Pedestals.tio"


class Pedestal_40deg_AC(Pedestal_File):
    def __init__(self):
        super().__init__()
        self.r0_path = "/Volumes/gct-jason/data_checs/d181203_erlangen/SN0038/ac_tf/40deg/Pedestals.tio"


class Pedestal_23deg_newFW(Pedestal_File):
    def __init__(self):
        super().__init__()
        self.r0_path = "/Volumes/gct-jason/data_checs/d181203_erlangen/SN0038/pedestal/Pedestal_23deg_newFW_r0.tio"


class Pedestal_23deg_newFW_waitlong(Pedestal_File):
    def __init__(self):
        super().__init__()
        self.r0_path = "/Volumes/gct-jason/data_checs/d181203_erlangen/SN0038/pedestal/Pedestal_23deg_newFW_waitlong_r0.tio"


def generate_ped_all():
    [generate_ped(f().r0_path) for f in child_subclasses(Pedestal_File)]
