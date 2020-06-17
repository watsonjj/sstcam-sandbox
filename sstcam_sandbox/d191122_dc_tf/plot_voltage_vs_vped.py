from sstcam_sandbox import get_plot, get_data
from CHECLabPy.core.io import HDF5Reader
from CHECLabPy.plotting.setup import Plotter
from TargetCalibSB.vped import VpedCalibrator
import re
import numpy as np
import pandas as pd
from IPython import embed


class VPEDPlot(Plotter):
    def plot(self, vped, voltage, label=None):
        self.ax.plot(vped, voltage, label=label)


def process(input_path, output_path):
    vped_calibrator = VpedCalibrator()
    vped_calibrator.load(input_path)

    n_channels, n_amplitudes = vped_calibrator.vped.shape
    p_vped = VPEDPlot()
    for channel in range(n_channels):
        p_vped.plot(vped_calibrator.vped[channel], vped_calibrator.voltage[channel])
    p_vped.ax.set_xlabel("VPED")
    p_vped.ax.set_ylabel("Voltage (mV)")
    p_vped.add_legend(loc='best')
    p_vped.save(output_path)


def process_single_channel(input_path, channel, output_path):
    vped_calibrator = VpedCalibrator()
    vped_calibrator.load(input_path)

    p_vped = VPEDPlot()
    p_vped.ax.set_xlabel("VPED")
    p_vped.ax.set_ylabel("Voltage (mV)")
    p_vped.add_legend(loc='best')
    p_vped.plot(vped_calibrator.vped[channel], vped_calibrator.voltage[channel])
    p_vped.save(output_path)


def process_different_temps(input_paths, channel, output_path):
    p_vped = VPEDPlot()

    reference_voltage = None
    for input_path in input_paths:
        regex_ped = re.search(r".+_([\d.]+)deg.h5", input_path)
        temperature = f"{float(regex_ped.group(1))} °C"

        vped_calibrator = VpedCalibrator()
        vped_calibrator.load(input_path)
        vped = vped_calibrator.vped[channel]
        voltage = vped_calibrator.voltage[channel]

        if reference_voltage is None:
            reference_voltage = voltage
            temperature = temperature + " (ref)"

        p_vped.plot(vped, voltage/reference_voltage, label=temperature)
    p_vped.ax.set_xlabel("VPED")
    p_vped.ax.set_ylabel("Relative Voltage")
    p_vped.add_legend(loc='best')
    p_vped.save(output_path)


def process_mean_std(input_path, mean_path, std_path):
    vped_calibrator = VpedCalibrator()
    vped_calibrator.load(input_path)

    vped = vped_calibrator.vped[0]
    mean = vped_calibrator.voltage.mean(0)
    std = vped_calibrator.voltage.std(0)
    std /= mean

    p_mean = VPEDPlot()
    p_mean.plot(vped, mean)
    p_mean.ax.set_xlabel("VPED")
    p_mean.ax.set_ylabel("Voltage Average Across Channels(mV)")
    p_mean.save(mean_path)

    p_std = VPEDPlot()
    p_std.plot(vped, std)
    p_std.ax.set_xlabel("VPED")
    p_std.ax.set_ylabel("Voltage Spread Across Channels(mV)")
    p_std.save(std_path)


def main():
    input_path = get_data("d191122_dc_tf/vped/VPED_13deg.h5")
    output_path = get_plot("d191122_dc_tf/vped/VPED_13deg.pdf")
    process(input_path, output_path)

    input_path = get_data("d191122_dc_tf/vped/VPED_23deg.h5")
    output_path = get_plot("d191122_dc_tf/vped/VPED_23deg.pdf")
    process(input_path, output_path)

    input_path = get_data("d191122_dc_tf/vped/VPED_33deg.h5")
    output_path = get_plot("d191122_dc_tf/vped/VPED_33deg.pdf")
    process(input_path, output_path)

    input_path = get_data("d191122_dc_tf/vped/VPED_43deg.h5")
    output_path = get_plot("d191122_dc_tf/vped/VPED_43deg.pdf")
    process(input_path, output_path)

    input_path = get_data("d191122_dc_tf/vped/VPED_23deg.h5")
    output_path = get_plot("d191122_dc_tf/vped/VPED_23deg_sc.pdf")
    process_single_channel(input_path, 8, output_path)

    input_paths = [
        get_data("d191122_dc_tf/vped/VPED_13deg.h5"),
        get_data("d191122_dc_tf/vped/VPED_23deg.h5"),
        get_data("d191122_dc_tf/vped/VPED_33deg.h5"),
        get_data("d191122_dc_tf/vped/VPED_43deg.h5"),
    ]
    output_path = get_plot("d191122_dc_tf/vped/temperature_comparison.pdf")
    process_different_temps(input_paths, 8, output_path)

    input_path = get_data("d191122_dc_tf/vped/VPED_23deg.h5")
    mean_path = get_plot("d191122_dc_tf/vped/VPED_23deg_mean.pdf")
    std_path = get_plot("d191122_dc_tf/vped/VPED_23deg_std.pdf")
    process_mean_std(input_path, mean_path, std_path)


if __name__ == '__main__':
    main()
