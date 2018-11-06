from CHECLabPySB.plotting.intensity_resolution import IntensityResolutionPlotter, \
    IntensityResolutionWRRPlotter
from CHECLabPySB.plotting.resolutions import ChargeMeanPlotter
from CHECLabPySB.scripts.d181031_sst_rfi.intensity_resolution import *
from CHECLabPySB.scripts.d181031_sst_rfi.mc_intensity_resolution import *
from CHECLabPySB import get_plot
import os
import numpy as np


class PlotHandler:
    def __init__(self, high_nsb=True, **kwargs):
        self.p_cr = IntensityResolutionPlotter(**kwargs)
        self.p_crwrr = IntensityResolutionWRRPlotter(**kwargs)
        self.p_mean = ChargeMeanPlotter(**kwargs)

        true = np.geomspace(4, 4000, 100)
        self.p_cr.plot_requirement(true)
        if high_nsb:
            self.p_cr.plot_requirement_highNSB(true)
        self.p_cr.plot_poisson(true)
        self.p_crwrr.plot_requirement(true)
        self.p_crwrr.plot_requirement_highNSB(true)
        self.p_crwrr.plot_poisson(true)

    def plot_average(self, file, label, poi, n_bins=40):
        self.p_cr.set_file(file)
        self.p_cr.plot_average(label, n_bins)
        self.p_cr.plot_scaling(label)
        self.p_crwrr.set_file(file)
        self.p_crwrr.plot_average(label, n_bins)
        self.p_crwrr.plot_scaling(label)
        self.p_mean.set_path(file.intensity_resolution_path)
        self.p_mean.plot_pixel(poi, label)

    def plot_pixel(self, file, label, poi):
        self.p_cr.set_file(file)
        self.p_cr.plot_pixel(poi, label)
        self.p_crwrr.set_file(file)
        self.p_crwrr.plot_pixel(poi, label)
        self.p_mean.set_path(file.intensity_resolution_path)
        self.p_mean.plot_pixel(poi, label)

    def plot_camera(self, file, label):
        self.p_cr.set_file(file)
        self.p_cr.plot_camera(label)
        self.p_crwrr.set_file(file)
        self.p_crwrr.plot_camera(label)
        self.p_mean.set_path(file.intensity_resolution_path)
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
        self.p_cr.add_legend(loc, frameon=False)
        self.p_crwrr.add_legend(loc)
        self.p_mean.add_legend(loc)

        self.p_cr.save(os.path.join(output_dir, "intensity_res.pdf"))
        self.p_crwrr.save(os.path.join(output_dir, "intensity_res_wrr.pdf"))
        self.p_mean.save(os.path.join(output_dir, "intensity_mean.pdf"))


def main():
    x_min = 2
    x_max = 4500

    # output_dir = get_plot("sst_rfi/plot_intensity_resolution/gainmatching")
    # path_dict = {
    #     "50mV-GM": d181010_LabSM_0MHz_50mV(),
    #     "100mV-GM": d181010_LabSM_0MHz_100mV(),
    #     "200mV-GM": d181010_LabSM_0MHz_200mV(),
    # }
    # ph = PlotHandler()
    # poi = list(path_dict.values())[0].poi
    # ph.plot_average_from_dict(path_dict, poi)
    # ph.p_cr.ax.set_xlim([x_min , x_max])
    # ph.p_crwrr.ax.set_ylim(top=2)
    # ph.save(output_dir)
    #
    # output_dir = get_plot("sst_rfi/plot_intensity_resolution/nsb_50mV")
    # path_dict = {
    #     # "0MHz": d181010_LabSM_0MHz_50mV(),
    #     "40MHz": d181010_LabSM_40MHz_50mV(),
    #     # "125MHz": d181010_LabSM_125MHz_50mV(),
    #     # "250MHz": d181010_LabSM_250MHz_50mV(),
    #     "1000MHz": d181010_LabSM_1000MHz_50mV(),
    # }
    # ph = PlotHandler()
    # poi = list(path_dict.values())[0].poi
    # ph.plot_average_from_dict(path_dict, poi)
    # ph.p_cr.ax.set_xlim([x_min , x_max])
    # ph.p_crwrr.ax.set_ylim(top=2)
    # ph.save(output_dir)

    # output_dir = get_plot("sst_rfi/plot_intensity_resolution/nsb_100mV")
    # path_dict = {
    #     "MCLab 40MHz": d180907_MCLab_opct40_40MHz(),
    #     "40MHz": d181010_LabSM_40MHz_100mV(),
    #     "1000MHz": d181010_LabSM_1000MHz_100mV(),
    # }
    # ph = PlotHandler()
    # poi = list(path_dict.values())[0].poi
    # ph.plot_average_from_dict(path_dict, poi)
    # ph.p_cr.ax.set_xlim([x_min , x_max])
    # ph.p_cr.ax.set_ylim([0.01, 20])
    # ph.p_crwrr.ax.set_ylim(top=2)
    # ph.save(output_dir)

    # output_dir = get_plot("sst_rfi/plot_intensity_resolution/lab_vs_mc")
    # path_dict = {
    #     "40MHz": d181010_LabSM_40MHz_100mV(),
    #     "MCLab 40MHz": d180907_MCLab_opct40_40MHz(),
    #     "Prod3": d181030_MCOnsky_Prod3(),
    #     "Prod4": d181030_MCOnsky_Prod4(),
    # }
    # ph = PlotHandler()
    # poi = list(path_dict.values())[0].poi
    # ph.plot_average_from_dict(path_dict, poi)
    # ph.p_cr.ax.set_xlim([x_min , x_max])
    # ph.p_cr.ax.set_ylim([0.01, 20])
    # ph.p_crwrr.ax.set_ylim(top=2)
    # ph.save(output_dir)

    # output_dir = get_plot("sst_rfi/plot_intensity_resolution/nsb_200mV")
    # path_dict = {
    #     # "0MHz": d181010_LabSM_0MHz_200mV(),
    #     "40MHz": d181010_LabSM_40MHz_200mV(),
    #     # "125MHz": d181010_LabSM_125MHz_200mV(),
    #     # "250MHz": d181010_LabSM_250MHz_200mV(),
    #     "1000MHz": d181010_LabSM_1000MHz_200mV(),
    # }
    # ph = PlotHandler()
    # poi = list(path_dict.values())[0].poi
    # ph.plot_average_from_dict(path_dict, poi)
    # ph.p_cr.ax.set_xlim([x_min , x_max])
    # ph.p_crwrr.ax.set_ylim(top=2)
    # ph.save(output_dir)

    output_dir = get_plot("sst_rfi/plot_intensity_resolution/mc_prod")
    path_dict = {
        "Prod3": d181030_MCOnsky_Prod3(),
        "Prod4": d181030_MCOnsky_Prod4(),
    }
    ph = PlotHandler(high_nsb=False, switch_backend=True)
    poi = list(path_dict.values())[0].poi
    ph.plot_camera_from_dict(path_dict)
    ph.p_cr.ax.set_xlim([x_min , x_max])
    ph.save(output_dir)


if __name__ == '__main__':
    main()
