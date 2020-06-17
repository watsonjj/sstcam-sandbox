from sstcam_sandbox import get_data, get_plot, HDF5Reader
from abc import abstractmethod, ABCMeta
import os
from CHECLabPy.utils.files import open_runlist_dl1, open_runlist_r1
import numpy as np


class File(metaclass=ABCMeta):
    def __init__(self, **kwargs):
        self.poi = 888
        self.dead = []
        self.runlist_path = None

    @property
    def waveforms_plot_dir(self):
        return get_plot("d181106_tf_investigations/waveforms/{}".format(self.__class__.__name__))

    @property
    def stats_path(self):
        return get_data("d181106_tf_investigations/stats/{}.h5".format(self.__class__.__name__))

    @property
    def fw_path(self):
        return get_data("d181021_charge_resolution/fw_calibration/{}.h5".format(
            self.__class__.__name__))

    @property
    def fw_plot_dir(self):
        return get_plot("d181021_charge_resolution/fw_calibration/{}".format(
            self.__class__.__name__))

    @property
    def ff_path(self):
        return get_data("d181021_charge_resolution/ff_coefficients/{}.h5".format(
            self.__class__.__name__))

    @property
    def ff_plot_dir(self):
        return get_plot("d181021_charge_resolution/ff_coefficients/{}".format(
            self.__class__.__name__))

    @property
    def charge_averages_path(self):
        return get_data("d181021_charge_resolution/charge_averages/{}.h5".format(
            self.__class__.__name__))

    @property
    def charge_resolution_path(self):
        return get_data("d181021_charge_resolution/charge_resolution/{}.h5".format(
            self.__class__.__name__))

    def get_dataframe(self, r1=False, **kwargs):
        if r1:
            df = open_runlist_r1(self.runlist_path, **kwargs)
        else:
            df = open_runlist_dl1(self.runlist_path, **kwargs)
        df['transmission'] = 1/df['fw_atten']

        with HDF5Reader(self.fw_path) as reader:
            fw_m = reader.read_metadata()['fw_m_camera']
            fw_merr = reader.read_metadata()['fw_merr_camera']

        df['expected'] = df['transmission'] * fw_m
        df['expected_err'] = df['transmission'] * fw_merr
        return df

    def get_run_with_illumination(self, illumination, r1=False):
        df = self.get_dataframe(r1=r1, open_readers=False)
        idxmin = np.abs(df['expected'] - illumination).idxmin()
        expected = df.loc[idxmin]['expected']
        epected_err = df.loc[idxmin]['expected_err']
        print("Run at illumination {:.3f} ± {:.3f} p.e. obtained".format(expected, epected_err))
        path = df.loc[idxmin]['path']
        return path, expected, epected_err


class Lab(File):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dead = [677, 293, 27, 1925, 1955]


class LabSM(Lab):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.poi = 30
        self.illumination_profile_path = None
        self.dead = []


class d181010_LabSM_0MHz_100mV_TFNone(LabSM):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.runlist_path = "/Volumes/gct-jason/data_checs/d181010_dynrange_sm/0MHz/100mV/tf_none/runlist.txt"
        self.spe_path = "/Volumes/gct-jason/data_checs/d181010_dynrange_sm/0MHz/100mV/tf_none/spe.h5"


class d181010_LabSM_0MHz_100mV_TFPchip(LabSM):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.runlist_path = "/Volumes/gct-jason/data_checs/d181010_dynrange_sm/0MHz/100mV/tf_pchip/runlist.txt"
        self.spe_path = "/Volumes/gct-jason/data_checs/d181010_dynrange_sm/0MHz/100mV/tf_pchip/spe.h5"


all_files = [
    d181010_LabSM_0MHz_100mV_TFNone(),
    d181010_LabSM_0MHz_100mV_TFPchip(),
]