from sstcam_sandbox import get_data, get_plot
from abc import abstractmethod, ABCMeta
from glob import glob
import re


def atoi(text):
    return int(text) if text.isdigit() else text


def natural_keys(text):
    """
    alist.sort(key=natural_keys) sorts in human order
    http://nedbatchelder.com/blog/200712/human_sorting.html
    (See Toothy's implementation in the comments)
    """
    return [atoi(c) for c in re.split('(\d+)', text)]


class File(metaclass=ABCMeta):
    def __init__(self, **kwargs):
        self.dead = []
        self.t_shift = None
        self.poi = 888


class d180514_DynRange_TFPoly(File):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.wf_paths = glob("/Volumes/gct-jason/data_checs/d180514_dynrange/tf_poly/*_r1.tio")
        self.wf_paths.sort(key=natural_keys)
        self.data_path = get_data("d181008_average_wf/d180514_DynRange_TFPoly.h5")
        self.plot_path = get_plot("d181008_average_wf/d180514_DynRange_TFPoly.pdf")
        self.t_shift = 43


class d181004_DynRange_SM_TFNone(File):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.wf_paths = glob("/Volumes/gct-jason/data_checs/d181004_dynrange_sm/tf_none/*_r1.tio")
        self.wf_paths.sort(key=natural_keys)
        self.data_path = get_data("d181008_average_wf/d181004_DynRange_SM_TFNone.h5")
        self.plot_path = get_plot("d181008_average_wf/d181004_DynRange_SM_TFNone.pdf")
        self.poi = 16
        self.t_shift = 43
