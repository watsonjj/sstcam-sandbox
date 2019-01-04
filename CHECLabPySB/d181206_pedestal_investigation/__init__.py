from glob import glob
import re
import os
from subprocess import call

class File:
    def __init__(self):
        self.r0_path = None


class Pedestal_SN0038_Erlangen_23deg_OldFW_3blocks(File):
    def __init__(self):
        super().__init__()
        self.r0_path = "/Volumes/gct-jason/data_checs/d181206_pedestal_investigation/SN0038/erlangen/pedestal_23deg_oldfw_3blocks.tio"


class Pedestal_SN0038_Erlangen_AC_23deg_OldFW_3blocks(File):
    def __init__(self):
        super().__init__()
        self.r0_path = "/Volumes/gct-jason/data_checs/d181206_pedestal_investigation/SN0038/erlangen/pedestal_ac_23deg_oldfw_3blocks.tio"


class Pedestal_SN0038_Erlangen_AC_40deg_OldFW_3blocks(File):
    def __init__(self):
        super().__init__()
        self.r0_path = "/Volumes/gct-jason/data_checs/d181206_pedestal_investigation/SN0038/erlangen/pedestal_ac_40deg_oldfw_3blocks.tio"


class Pedestal_SN0038_Erlangen_23deg_NewFW_3blocks(File):
    def __init__(self):
        super().__init__()
        self.r0_path = "/Volumes/gct-jason/data_checs/d181206_pedestal_investigation/SN0038/erlangen/pedestal_23deg_newfw_3blocks.tio"


class Pedestal_SN0038_Erlangen_23deg_NewFW_waitlong_3blocks(File):
    def __init__(self):
        super().__init__()
        self.r0_path = "/Volumes/gct-jason/data_checs/d181206_pedestal_investigation/SN0038/erlangen/pedestal_23deg_newfw_waitlong_3blocks.tio"


class Pedestal_SN0038_Erlangen_23deg_NewFW_4blocks(File):
    def __init__(self):
        super().__init__()
        self.r0_path = "/Volumes/gct-jason/data_checs/d181206_pedestal_investigation/SN0038/erlangen/pedestal_23deg_newfw_4blocks.tio"


class Pedestal_SN0038_Erlangen_AC_23deg_NewFW_4blocks(File):
    def __init__(self):
        super().__init__()
        self.r0_path = "/Volumes/gct-jason/data_checs/d181206_pedestal_investigation/SN0038/erlangen/pedestal_ac_23deg_newfw_4blocks.tio"


class Pedestal_SN0038_Erlangen_30deg_NewFW_4blocks(File):
    def __init__(self):
        super().__init__()
        self.r0_path = "/Volumes/gct-jason/data_checs/d181206_pedestal_investigation/SN0038/erlangen/pedestal_30deg_newfw_4blocks.tio"


class Pedestal_SN0038_MPIK_23deg_NewFW_4blocks_500Hz(File):
    def __init__(self):
        super().__init__()
        self.r0_path = "/Volumes/gct-jason/data_checs/d181206_pedestal_investigation/SN0038/mpik/Pedestal_23deg_newfw_4blocks_500Hz_r0.tio"


class Pedestal_SN0038_MPIK_23deg_NewFW_4blocks_1000Hz(File):
    def __init__(self):
        super().__init__()
        self.r0_path = "/Volumes/gct-jason/data_checs/d181206_pedestal_investigation/SN0038/mpik/Pedestal_23deg_newfw_4blocks_1000Hz_r0.tio"


class Pedestal_SN0038_MPIK_23deg_NewFW_4blocks_2000Hz(File):
    def __init__(self):
        super().__init__()
        self.r0_path = "/Volumes/gct-jason/data_checs/d181206_pedestal_investigation/SN0038/mpik/Pedestal_23deg_newfw_4blocks_2000Hz_r0.tio"


class Pedestal_SN0038_MPIK_23deg_NewFW_4blocks_4000Hz(File):
    def __init__(self):
        super().__init__()
        self.r0_path = "/Volumes/gct-jason/data_checs/d181206_pedestal_investigation/SN0038/mpik/Pedestal_23deg_newfw_4blocks_4000Hz_r0.tio"


class Pedestal_SN0038_MPIK_23deg_NewFW_4blocks_3000Hz_cvped(File):
    def __init__(self):
        super().__init__()
        self.r0_path = "/Volumes/gct-jason/data_checs/d181206_pedestal_investigation/SN0038/mpik/Pedestal_23deg_newfw_4blocks_3000Hz_cvped_r0.tio"


class Pedestal_SN0038_MPIK_23deg_NewFW_4blocks_3500Hz_cvped(File):
    def __init__(self):
        super().__init__()
        self.r0_path = "/Volumes/gct-jason/data_checs/d181206_pedestal_investigation/SN0038/mpik/Pedestal_23deg_newfw_4blocks_3500Hz_cvped_r0.tio"


class Pedestal_SN0038_MPIK_23deg_NewFW_4blocks_4000Hz_cvped(File):
    def __init__(self):
        super().__init__()
        self.r0_path = "/Volumes/gct-jason/data_checs/d181206_pedestal_investigation/SN0038/mpik/Pedestal_23deg_newfw_4blocks_4000Hz_cvped_r0.tio"


class Pedestal_Adrian(File):
    def __init__(self):
        super().__init__()
        self.r0_path = "/Users/Jason/Downloads/pedestal_new_r0.tio"

