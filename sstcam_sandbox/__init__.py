import os
import pandas as pd
import warnings
from CHECLabPy.utils.files import create_directory

_ROOT = os.path.abspath(os.path.dirname(__file__))
_DATA = os.path.expanduser(os.path.join(os.environ['dir_data'], "sstcam_sandbox/data"))
_PLOT = os.path.expanduser(os.path.join(os.environ['dir_data'], "sstcam_sandbox/plots"))

_LARGE = os.path.expanduser(os.environ['dir_data_large'])
_CHECS = os.path.expanduser(os.path.join(_LARGE, "data_checs"))
_SIMTEL = os.path.expanduser(os.path.join(_LARGE, "sim_telarray"))
_ASTRI2019 = os.path.expanduser(os.path.join(_LARGE, "astri_onsky_archive"))


def get_data(path):
    data_path = os.path.join(_DATA, path)
    create_directory(os.path.dirname(data_path))
    return data_path


def get_plot(path):
    plot_path = os.path.join(_PLOT, path)
    create_directory(os.path.dirname(plot_path))
    return plot_path


def get_checs(path):
    path = os.path.join(_CHECS, path)
    return path


def get_simtel(path):
    path = os.path.join(_SIMTEL, path)
    return path


def get_astri_2019(path):
    path = os.path.join(_ASTRI2019, path)
    return path
