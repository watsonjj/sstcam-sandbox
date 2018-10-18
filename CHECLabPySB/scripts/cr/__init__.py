from CHECLabPySB import get_data, get_plot, HDF5Reader
from abc import abstractmethod, ABCMeta
import os
from CHECLabPy.utils.files import open_runlist_dl1, open_runlist_r1
import numpy as np


class File(metaclass=ABCMeta):
    def __init__(self, **kwargs):
        self.poi = 888
        self.dead = []

    @property
    def spe_runlist_path(self):
        return self.runlist_path
    #
    # @property
    # def charge_averages_path(self):
    #     return os.path.join(os.path.dirname(self.runlist_path), "charge_averages.h5")
    #
    # @property
    # def charge_resolution_path(self):
    #     return os.path.join(os.path.dirname(self.runlist_path), "charge_resolution.h5")
    #
    # @property
    # def charge_before_after_path(self):
    #     return os.path.join(os.path.dirname(self.runlist_path), "charge_before_after.h5")
    #
    # @property
    # def spe_files(self):
    #     df = open_runlist_dl1(self.runlist_path, open_readers=False)
    #     path_list = df.iloc[-7:-4]['path'].tolist()
    #     return path_list
    #
    # @property
    # def reader_list(self):
    #     return open_runlist_dl1(self.runlist_path)['reader'].tolist()
    #
    # # @abstractmethod
    # # def is_abstract(self):
    # #     return True
    #
    # def get_dataframe(self, r1=False, **kwargs):
    #     if r1:
    #         df = open_runlist_r1(self.runlist_path, **kwargs)
    #     else:
    #         df = open_runlist_dl1(self.runlist_path, **kwargs)
    #     df['transmission'] = 1/df['fw_atten']
    #
    #     with HDF5Reader(self.fw_path) as reader:
    #         fw_m = reader.read_metadata()['fw_m_camera']
    #         fw_merr = reader.read_metadata()['fw_merr_camera']
    #
    #     df['expected'] = df['transmission'] * fw_m
    #     df['expected_err'] = df['transmission'] * fw_merr
    #     return df
    #
    # def get_run_with_illumination(self, illumination, r1=False):
    #     df = self.get_dataframe(r1=r1, open_readers=False)
    #     idxmin = np.abs(df['expected'] - illumination).idxmin()
    #     expected = df.loc[idxmin]['expected']
    #     epected_err = df.loc[idxmin]['expected_err']
    #     print("Run at illumination {:.3f} ± {:.3f} p.e. obtained".format(expected, epected_err))
    #     path = df.loc[idxmin]['path']
    #     return path, expected, epected_err
    #
    # def get_n_nearest_illuminations(self, illumination, n, r1=False):
    #     df = self.get_dataframe(r1=r1, open_readers=False)
    #     df['nearest'] = np.abs(df['expected'] - illumination)
    #     df.sort_values('nearest', inplace=True)
    #     df_nearest = df.iloc[:n]
    #     return df_nearest


class Lab(File):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.illumination_profile_path = get_data("cr/illumination_profile/d180907_MC.h5")  # TODO: get lab_illumination_profile_correction.h5
        self.dead = [677, 293, 27, 1925, 1955]

    @property
    def fw_path(self):
        return get_data("cr/fw_calibration/{}.h5".format(self.__class__.__name__))

    @property
    def fw_plot_dir(self):
        return get_plot("cr/fw_calibration/{}".format(self.__class__.__name__))

    @property
    def ff_path(self):
        return get_data("cr/ff_coefficients/{}.h5".format(self.__class__.__name__))

    @property
    def ff_plot_dir(self):
        return get_plot("cr/ff_coefficients/{}".format(self.__class__.__name__))

    @property
    def charge_averages_path(self):
        return get_data("cr/charge_averages/{}.h5".format(self.__class__.__name__))

    @property
    def charge_resolution_path(self):
        return get_data("cr/charge_resolution/{}.h5".format(self.__class__.__name__))


class d180514_Lab_TFNone(Lab):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.runlist_path = "/Volumes/gct-jason/data_checs/d180514_dynrange/tf_none/runlist.txt"
        self.spe_path = "/Volumes/gct-jason/data_checs/d180514_dynrange/tf_none/spe.h5"


class d180514_Lab_TFPoly(Lab):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.runlist_path = "/Volumes/gct-jason/data_checs/d180514_dynrange/tf_poly/runlist.txt"
        self.spe_path = "/Volumes/gct-jason/data_checs/d180514_dynrange/tf_poly/spe.h5"


class LabSM(Lab):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.poi = 2
        self.illumination_profile_path = None
        self.dead = []


class d181010_LabSM_0MHz_50mV_TFPoly(LabSM):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.runlist_path = "/Volumes/gct-jason/data_checs/d181010_dynrange_sm/0MHz/50mV/tf_poly/runlist.txt"
        self.spe_path = "/Volumes/gct-jason/data_checs/d181010_dynrange_sm/0MHz/50mV/tf_poly/spe.h5"


class d181010_LabSM_0MHz_100mV_TFPoly(LabSM):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.runlist_path = "/Volumes/gct-jason/data_checs/d181010_dynrange_sm/0MHz/100mV/tf_poly/runlist.txt"
        self.spe_path = "/Volumes/gct-jason/data_checs/d181010_dynrange_sm/0MHz/100mV/tf_poly/spe.h5"


class d181010_LabSM_0MHz_200mV_TFPoly(LabSM):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.runlist_path = "/Volumes/gct-jason/data_checs/d181010_dynrange_sm/0MHz/200mV/tf_poly/runlist.txt"
        self.spe_path = "/Volumes/gct-jason/data_checs/d181010_dynrange_sm/0MHz/200mV/tf_poly/spe.h5"


all_files = [
    # d180514_Lab_TFNone(),
    # d180514_Lab_TFPoly(),
    d181010_LabSM_0MHz_50mV_TFPoly(),
    d181010_LabSM_0MHz_100mV_TFPoly(),
    d181010_LabSM_0MHz_200mV_TFPoly(),
]
