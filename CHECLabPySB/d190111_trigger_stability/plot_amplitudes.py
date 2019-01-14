from CHECLabPySB.plotting.setup import Plotter
from CHECLabPySB import get_plot, get_data, HDF5Reader
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from IPython import embed
from datetime import datetime
import os


class TimePlotter(Plotter):
    def __init__(self, ylabel):
        super().__init__()
        self.ylabel = ylabel

    def plot(self, x, y, color, label=None):
        x = (x - x[0]).astype(datetime) * 1E-9 / 3600
        self.ax.plot(x, y, color=color, label=label)

    def finish(self):
        self.ax.legend(loc='best')
        self.ax.set_xlabel("Time (hours)")
        self.ax.set_ylabel(self.ylabel)


def process_pix(input_path, output_dir):
    with HDF5Reader(input_path) as reader:
        df = reader.read("data")
        metadata = reader.read_metadata()

    p_amplitude = TimePlotter("Waveform Maximum (mV)")
    p_baseline = TimePlotter("Baseline (average of first 20 samples) (mV)")

    for superpixel, group_sp in df.groupby("superpixel"):
        color = next(p_amplitude.ax._get_lines.prop_cycler)['color']
        sp_plotted = []
        for pixel, group_pix in group_sp.groupby("pixel"):
            group_pix = group_pix.set_index('t_cpu')
            group_pix = group_pix.resample("60S").mean()

            x = group_pix.index.values
            y_amp = group_pix['amplitude'].values
            y_base = group_pix['baseline'].values
            label = metadata["sp{}".format(superpixel)] \
                if superpixel not in sp_plotted else None

            p_amplitude.plot(x, y_amp, color, label)
            p_baseline.plot(x, y_base, color, label)

            sp_plotted.append(superpixel)

    p_amplitude.save(os.path.join(output_dir, "amplitude.pdf"))
    p_baseline.save(os.path.join(output_dir, "baseline.pdf"))


def process_sp(input_path, output_dir):
    with HDF5Reader(input_path) as reader:
        df = reader.read("data_sum")
        metadata = reader.read_metadata()

    p_amplitude = TimePlotter("Waveform Maximum (summed WF) (mV)")
    p_baseline = TimePlotter("Baseline (summed WF) (average of first 20 samples) (mV)")

    for superpixel, group_sp in df.groupby("superpixel"):
        color = next(p_amplitude.ax._get_lines.prop_cycler)['color']
        group_sp = group_sp.set_index('t_cpu')
        group_sp = group_sp.resample("60S").mean()

        x = group_sp.index.values
        y_amp = group_sp['amplitude'].values
        y_base = group_sp['baseline'].values
        label = metadata["sp{}".format(superpixel)]

        p_amplitude.plot(x, y_amp, color, label)
        p_baseline.plot(x, y_base, color, label)

    p_amplitude.save(os.path.join(output_dir, "amplitude_sum.pdf"))
    p_baseline.save(os.path.join(output_dir, "baseline_sum.pdf"))


def main():
    input_path = get_data("d190111_trigger_stability/extract_amplitudes.h5")
    output_dir = get_plot("d190111_trigger_stability/plot_amplitudes")
    process_pix(input_path, output_dir)
    process_sp(input_path, output_dir)


if __name__ == '__main__':
    main()
