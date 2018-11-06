from CHECLabPySB.plotting.resolutions import ChargeResolutionPlotter, \
    ChargeResolutionWRRPlotter, ChargeMeanPlotter
from CHECLabPySB.scripts.d181021_charge_resolution import *
from CHECLabPySB import get_plot, HDF5Reader, get_data
import os
import numpy as np


class PlotHandler:
    def __init__(self, **kwargs):
        self.p_cr = ChargeResolutionPlotter(**kwargs)
        self.p_crwrr = ChargeResolutionWRRPlotter(**kwargs)
        self.p_mean = ChargeMeanPlotter(**kwargs)

        true = np.geomspace(0.1, 1000, 100)
        self.p_cr.plot_requirement(true)
        self.p_cr.plot_poisson(true)
        self.p_crwrr.plot_requirement(true)
        self.p_crwrr.plot_poisson(true)

    def plot_average(self, file, label, poi, n_bins=40):
        self.p_cr.set_file(file)
        self.p_cr.plot_average(label, n_bins)
        self.p_crwrr.set_file(file)
        self.p_crwrr.plot_average(label, n_bins)

        self.p_mean.set_path(file.charge_resolution_path)
        self.p_mean.plot_pixel(poi, label)

    def plot_pixel(self, file, label, poi):
        self.p_cr.set_file(file)
        self.p_cr.plot_pixel(poi, label)
        self.p_crwrr.set_file(file)
        self.p_crwrr.plot_pixel(poi, label)
        self.p_mean.set_path(file.charge_resolution_path)
        self.p_mean.plot_pixel(poi, label)

    def plot_camera(self, file, label):
        self.p_cr.set_file(file)
        self.p_cr.plot_camera(label)
        self.p_crwrr.set_file(file)
        self.p_crwrr.plot_camera(label)
        self.p_mean.set_path(file.charge_resolution_path)
        self.p_mean.plot_camera(label)

    def plot_average_from_dict(self, path_dict, poi):
        for label, path in path_dict.items():
            self.plot_average(path, label, poi)

    def plot_pixel_from_dict(self, path_dict, poi):
        for label, path in path_dict.items():
            self.plot_pixel(path, label, poi)

    def plot_camera_from_dict(self, path_dict):
        for label, path in path_dict.items():
            self.plot_camera(path, label)

    def save(self, output_dir, loc="best"):
        self.p_cr.add_legend(loc)
        self.p_crwrr.add_legend(loc)
        self.p_mean.add_legend(loc)

        self.p_cr.save(os.path.join(output_dir, "charge_res.pdf"))
        self.p_crwrr.save(os.path.join(output_dir, "charge_res_wrr.pdf"))
        self.p_mean.save(os.path.join(output_dir, "charge_mean.pdf"))


def main():

    output_dir = get_plot("charge_resolution/charge_resolution/d181010_LabSM_0MHz")
    path_dict = {
        "50mV-GM": d181010_LabSM_0MHz_50mV_TFMix(),
        "100mV-GM": d181010_LabSM_0MHz_100mV_TFMix(),
        "200mV-GM": d181010_LabSM_0MHz_200mV_TFMix(),
    }
    ph = PlotHandler()
    poi = list(path_dict.values())[0].poi
    ph.plot_average_from_dict(path_dict, poi)
    ph.p_crwrr.ax.set_ylim(top=2)
    ph.save(output_dir)

    output_dir = get_plot("charge_resolution/charge_resolution/d181010_LabSM_125MHz")
    path_dict = {
        "50mV-GM": d181010_LabSM_125MHz_50mV_TFMix(),
        "100mV-GM": d181010_LabSM_125MHz_100mV_TFMix(),
        "200mV-GM": d181010_LabSM_125MHz_200mV_TFMix(),
    }
    ph = PlotHandler()
    poi = list(path_dict.values())[0].poi
    ph.plot_average_from_dict(path_dict, poi)
    ph.p_crwrr.ax.set_ylim(top=2)
    ph.save(output_dir)

    output_dir = get_plot("charge_resolution/charge_resolution/tf_comparison")
    path_dict = {
        "No TF": d181010_LabSM_0MHz_100mV_TFNone(),
        "TF (default)": d181010_LabSM_0MHz_100mV_TFPchip(),
        # "TF (polynomial fit)": d181010_LabSM_0MHz_100mV_TFPoly(),
        "TF (mix between the two)": d181010_LabSM_0MHz_100mV_TFMix(),
    }
    ph = PlotHandler()
    poi = list(path_dict.values())[0].poi
    ph.plot_average_from_dict(path_dict, poi)
    ph.p_crwrr.ax.set_ylim(top=2)
    ph.save(output_dir)

    output_dir = get_plot("charge_resolution/charge_resolution/nsb")
    path_dict = {
        "0MHz": d181010_LabSM_0MHz_100mV_TFMix(),
        "40MHz": d181010_LabSM_40MHz_100mV_TFMix(),
        "125MHz": d181010_LabSM_125MHz_100mV_TFMix(),
        "250MHz": d181010_LabSM_250MHz_100mV_TFMix(),
        "1000MHz": d181010_LabSM_1000MHz_100mV_TFMix(),
    }
    ph = PlotHandler()
    poi = list(path_dict.values())[0].poi
    ph.plot_average_from_dict(path_dict, poi)
    ph.p_crwrr.ax.set_ylim(top=2)
    ph.save(output_dir)

    output_dir = get_plot("charge_resolution/charge_resolution/nsb_selfped")
    path_dict = {
        "0MHz": d181010_LabSM_0MHz_100mV_SelfPed(),
        "40MHz": d181010_LabSM_40MHz_100mV_SelfPed(),
        "125MHz": d181010_LabSM_125MHz_100mV_SelfPed(),
        "250MHz": d181010_LabSM_250MHz_100mV_SelfPed(),
        "1000MHz": d181010_LabSM_1000MHz_100mV_SelfPed(),
    }
    ph = PlotHandler()
    poi = list(path_dict.values())[0].poi
    ph.plot_average_from_dict(path_dict, poi)
    ph.p_crwrr.ax.set_ylim(top=2)
    ph.save(output_dir)


if __name__ == '__main__':
    main()
