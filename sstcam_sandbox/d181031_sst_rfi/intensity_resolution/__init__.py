from sstcam_sandbox import get_data, get_plot
from sstcam_sandbox.old.io import HDF5Reader
from abc import abstractmethod, ABCMeta
import os
from CHECLabPy.utils.files import open_runlist_dl1, open_runlist_r1
import numpy as np


class File(metaclass=ABCMeta):
    def __init__(self, **kwargs):
        self.poi = 0
        self.dead = []
        self.runlist_path = None
        self.pde = None

    @property
    def spe_runlist_path(self):
        return self.runlist_path

    @property
    def fw_path(self):
        return get_data("d181031_sst_rfi/intensity_resolution/fw_calibration/{}.h5".format(self.__class__.__name__))

    @property
    def fw_plot_dir(self):
        return get_plot("d181031_sst_rfi/intensity_resolution/fw_calibration/{}".format(self.__class__.__name__))

    @property
    def ff_path(self):
        return get_data("d181031_sst_rfi/intensity_resolution/ff_coefficients/{}.h5".format(self.__class__.__name__))

    @property
    def ff_plot_dir(self):
        return get_plot("d181031_sst_rfi/intensity_resolution/ff_coefficients/{}".format(self.__class__.__name__))

    @property
    def charge_averages_path(self):
        return get_data("d181031_sst_rfi/intensity_resolution/charge_averages/{}.h5".format(self.__class__.__name__))

    @property
    def intensity_resolution_path(self):
        return get_data("d181031_sst_rfi/intensity_resolution/intensity_resolution/{}.h5".format(self.__class__.__name__))

    @property
    def fit_intensity_res_path(self):
        return get_data("d181031_sst_rfi/intensity_resolution/fit_intensity_res/{}.h5".format(self.__class__.__name__))

    @property
    def fit_intensity_res_plot_path(self):
        return get_plot("d181031_sst_rfi/intensity_resolution/fit_intensity_res/{}.pdf".format(self.__class__.__name__))

    @property
    def saturation_recovery_path(self):
        return get_data("d181031_sst_rfi/intensity_resolution/saturation_recovery/{}.h5".format(self.__class__.__name__))

    @property
    def saturation_recovery_plot_path(self):
        return get_plot("d181031_sst_rfi/intensity_resolution/saturation_recovery/{}.pdf".format(self.__class__.__name__))


class MCLab(File):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.illumination_profile_path = get_data("d181031_sst_rfi/intensity_resolution/illumination_profile/d180907_MC.h5")
        self.dead = []


class d180907_MCLab_opct40_0MHz(MCLab):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.runlist_path = "/Volumes/gct-jason/sim_telarray/d180907_dynrange/opct40/0MHz/runlist.txt"
        self.spe_path = "/Volumes/gct-jason/sim_telarray/d180907_dynrange/opct40/0MHz/spe.h5"
        self.pde = 0.345 * 0.537


class d180907_MCLab_opct40_40MHz(MCLab):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.runlist_path = "/Volumes/gct-jason/sim_telarray/d180907_dynrange/opct40/40MHz/runlist.txt"
        self.spe_path = None
        self.pde = 0.345 * 0.537

    @property
    def fw_path(self):
        return get_data("d181031_sst_rfi/intensity_resolution/fw_calibration/{}.h5".format(d180907_MCLab_opct40_0MHz.__name__))


class Lab(File):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.illumination_profile_path = get_data("d181031_sst_rfi/intensity_resolution/illumination_profile/d180907_MC.h5")  # TODO: get lab_illumination_profile_correction.h5
        self.dead = [677, 293, 27, 1925, 1955]


class LabSM(Lab):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.poi = 30
        self.illumination_profile_path = None
        self.dead = []


class d181010_LabSM_0MHz_50mV(LabSM):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.runlist_path = "/Volumes/gct-jason/data_checs/d181010_dynrange_sm/0MHz/50mV/selfped/runlist.txt"
        self.spe_path = "/Volumes/gct-jason/data_checs/d181010_dynrange_sm/0MHz/50mV/selfped/spe.h5"


class d181010_LabSM_0MHz_100mV(LabSM):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.runlist_path = "/Volumes/gct-jason/data_checs/d181010_dynrange_sm/0MHz/100mV/selfped/runlist.txt"
        self.spe_path = "/Volumes/gct-jason/data_checs/d181010_dynrange_sm/0MHz/100mV/selfped/spe.h5"


class d181010_LabSM_0MHz_200mV(LabSM):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.runlist_path = "/Volumes/gct-jason/data_checs/d181010_dynrange_sm/0MHz/200mV/selfped/runlist.txt"
        self.spe_path = "/Volumes/gct-jason/data_checs/d181010_dynrange_sm/0MHz/200mV/selfped/spe.h5"


class d181010_LabSM_40MHz_50mV(LabSM):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.runlist_path = "/Volumes/gct-jason/data_checs/d181010_dynrange_sm/40MHz/50mV/selfped/runlist.txt"
        self.spe_path = "/Volumes/gct-jason/data_checs/d181010_dynrange_sm/40MHz/50mV/selfped/spe.h5"

    @property
    def fw_path(self):
        return get_data("d181031_sst_rfi/intensity_resolution/fw_calibration/{}.h5".format(d181010_LabSM_0MHz_50mV.__name__))


class d181010_LabSM_40MHz_100mV(LabSM):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.runlist_path = "/Volumes/gct-jason/data_checs/d181010_dynrange_sm/40MHz/100mV/selfped/runlist.txt"
        self.spe_path = "/Volumes/gct-jason/data_checs/d181010_dynrange_sm/40MHz/100mV/selfped/spe.h5"

    @property
    def fw_path(self):
        return get_data("d181031_sst_rfi/intensity_resolution/fw_calibration/{}.h5".format(d181010_LabSM_0MHz_100mV.__name__))


class d181010_LabSM_40MHz_200mV(LabSM):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.runlist_path = "/Volumes/gct-jason/data_checs/d181010_dynrange_sm/40MHz/200mV/selfped/runlist.txt"
        self.spe_path = "/Volumes/gct-jason/data_checs/d181010_dynrange_sm/40MHz/200mV/selfped/spe.h5"

    @property
    def fw_path(self):
        return get_data("d181031_sst_rfi/intensity_resolution/fw_calibration/{}.h5".format(d181010_LabSM_0MHz_200mV.__name__))


class d181010_LabSM_125MHz_50mV(LabSM):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.runlist_path = "/Volumes/gct-jason/data_checs/d181010_dynrange_sm/125MHz/50mV/selfped/runlist.txt"
        self.spe_path = "/Volumes/gct-jason/data_checs/d181010_dynrange_sm/125MHz/50mV/selfped/spe.h5"

    @property
    def fw_path(self):
        return get_data("d181031_sst_rfi/intensity_resolution/fw_calibration/{}.h5".format(d181010_LabSM_0MHz_50mV.__name__))


class d181010_LabSM_125MHz_100mV(LabSM):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.runlist_path = "/Volumes/gct-jason/data_checs/d181010_dynrange_sm/125MHz/100mV/selfped/runlist.txt"
        self.spe_path = "/Volumes/gct-jason/data_checs/d181010_dynrange_sm/125MHz/100mV/selfped/spe.h5"

    @property
    def fw_path(self):
        return get_data("d181031_sst_rfi/intensity_resolution/fw_calibration/{}.h5".format(d181010_LabSM_0MHz_100mV.__name__))


class d181010_LabSM_125MHz_200mV(LabSM):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.runlist_path = "/Volumes/gct-jason/data_checs/d181010_dynrange_sm/125MHz/200mV/selfped/runlist.txt"
        self.spe_path = "/Volumes/gct-jason/data_checs/d181010_dynrange_sm/125MHz/200mV/selfped/spe.h5"

    @property
    def fw_path(self):
        return get_data("d181031_sst_rfi/intensity_resolution/fw_calibration/{}.h5".format(d181010_LabSM_0MHz_200mV.__name__))


class d181010_LabSM_250MHz_50mV(LabSM):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.runlist_path = "/Volumes/gct-jason/data_checs/d181010_dynrange_sm/250MHz/50mV/selfped/runlist.txt"
        self.spe_path = "/Volumes/gct-jason/data_checs/d181010_dynrange_sm/250MHz/50mV/selfped/spe.h5"

    @property
    def fw_path(self):
        return get_data("d181031_sst_rfi/intensity_resolution/fw_calibration/{}.h5".format(d181010_LabSM_0MHz_50mV.__name__))


class d181010_LabSM_250MHz_100mV(LabSM):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.runlist_path = "/Volumes/gct-jason/data_checs/d181010_dynrange_sm/250MHz/100mV/selfped/runlist.txt"
        self.spe_path = "/Volumes/gct-jason/data_checs/d181010_dynrange_sm/250MHz/100mV/selfped/spe.h5"

    @property
    def fw_path(self):
        return get_data("d181031_sst_rfi/intensity_resolution/fw_calibration/{}.h5".format(d181010_LabSM_0MHz_100mV.__name__))


class d181010_LabSM_250MHz_200mV(LabSM):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.runlist_path = "/Volumes/gct-jason/data_checs/d181010_dynrange_sm/250MHz/200mV/selfped/runlist.txt"
        self.spe_path = "/Volumes/gct-jason/data_checs/d181010_dynrange_sm/250MHz/200mV/selfped/spe.h5"

    @property
    def fw_path(self):
        return get_data("d181031_sst_rfi/intensity_resolution/fw_calibration/{}.h5".format(d181010_LabSM_0MHz_200mV.__name__))


class d181010_LabSM_1000MHz_50mV(LabSM):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.runlist_path = "/Volumes/gct-jason/data_checs/d181010_dynrange_sm/1000MHz/50mV/selfped/runlist.txt"
        self.spe_path = "/Volumes/gct-jason/data_checs/d181010_dynrange_sm/1000MHz/50mV/selfped/spe.h5"

    @property
    def fw_path(self):
        return get_data("d181031_sst_rfi/intensity_resolution/fw_calibration/{}.h5".format(d181010_LabSM_0MHz_50mV.__name__))


class d181010_LabSM_1000MHz_100mV(LabSM):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.runlist_path = "/Volumes/gct-jason/data_checs/d181010_dynrange_sm/1000MHz/100mV/selfped/runlist.txt"
        self.spe_path = "/Volumes/gct-jason/data_checs/d181010_dynrange_sm/1000MHz/100mV/selfped/spe.h5"

    @property
    def fw_path(self):
        return get_data("d181031_sst_rfi/intensity_resolution/fw_calibration/{}.h5".format(d181010_LabSM_0MHz_100mV.__name__))


class d181010_LabSM_1000MHz_200mV(LabSM):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.runlist_path = "/Volumes/gct-jason/data_checs/d181010_dynrange_sm/1000MHz/200mV/selfped/runlist.txt"
        self.spe_path = "/Volumes/gct-jason/data_checs/d181010_dynrange_sm/1000MHz/200mV/selfped/spe.h5"

    @property
    def fw_path(self):
        return get_data("d181031_sst_rfi/intensity_resolution/fw_calibration/{}.h5".format(d181010_LabSM_0MHz_200mV.__name__))


fw_files = [
    # d180907_MCLab_opct40_0MHz(),
    # d181010_LabSM_0MHz_50mV(),
    # d181010_LabSM_0MHz_100mV(),
    # d181010_LabSM_0MHz_200mV(),
]


all_files = [
    # d180907_MCLab_opct40_0MHz(),
    d180907_MCLab_opct40_40MHz(),
    # d181010_LabSM_0MHz_50mV(),
    # d181010_LabSM_0MHz_100mV(),
    # d181010_LabSM_0MHz_200mV(),
    # d181010_LabSM_40MHz_50mV(),
    d181010_LabSM_40MHz_100mV(),
    # d181010_LabSM_40MHz_200mV(),
    # d181010_LabSM_125MHz_50mV(),
    # d181010_LabSM_125MHz_100mV(),
    # d181010_LabSM_125MHz_200mV(),
    # d181010_LabSM_250MHz_50mV(),
    # d181010_LabSM_250MHz_100mV(),
    # d181010_LabSM_250MHz_200mV(),
    # d181010_LabSM_1000MHz_50mV(),
    d181010_LabSM_1000MHz_100mV(),
    # d181010_LabSM_1000MHz_200mV(),
]

fit_files = [
    d181010_LabSM_40MHz_100mV(),
    d181010_LabSM_1000MHz_100mV(),
]