from sstcam_sandbox.plotting.setup import Plotter
from sstcam_sandbox.d190117_trigger_stability import *
from sstcam_sandbox import get_plot, get_data, HDF5Reader
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from IPython import embed
from datetime import datetime
import os
from tqdm import tqdm


class TimePlotter(Plotter):
    def __init__(self, ylabel, **kwargs):
        super().__init__(**kwargs)
        self.ylabel = ylabel

    def plot(self, x, y, color, label=None):
        x = (x - x[0]).astype(datetime) * 1E-9 / 3600
        self.ax.plot(x, y, color=color, label=label, alpha=0.5)

    def finish(self):
        # self.ax.legend(loc='best')
        self.ax.set_xlabel("Time (hours)")
        self.ax.set_ylabel(self.ylabel)


def process(input_path, output_dir, spoi):
    with HDF5Reader(input_path) as reader:
        df = reader.read("data")
        mapping = reader.read_mapping()
        superpixels = mapping['superpixel'].values.astype(np.int)
        df['superpixel'] = superpixels[df['pixel']]

    p_amplitude = TimePlotter("Waveform Maximum (mV)", switch_backend=True)
    p_amplitudesp = TimePlotter("Superpixel-Waveform Maximum (mV)", switch_backend=True)

    spoi.extend([0, 1])

    desc = "Plotting superpixels"
    spoi = np.arange(512)
    for superpixel in tqdm(spoi, total=len(spoi), desc=desc):
        df_sp = df.loc[df['superpixel'] == superpixel]
        df_sp = (df_sp
                 .set_index('t_cpu')
                 .groupby([pd.Grouper(freq='387S'), 'pixel'])
                 .mean()
                 .reset_index()
                 )

        color = next(p_amplitude.ax._get_lines.prop_cycler)['color']
        label = "SP={}".format(superpixel)

        # if df_sp['amplitude_sp'].max() < 10:
        #     continue
        # elif df_sp['amplitude_sp'].max() > 700:
        # min_ = df_sp['amplitude_sp'].min()
        # max_ = df_sp['amplitude_sp'].max()
        # mean = df_sp['amplitude_sp'].mean()
        # low = 0.8 * mean
        # high = 1.2 * mean
        # embed()
        # if (min_ > low) & (max_ < high):
        #     continue
        # if df_sp['amplitude_sp'].values[0] < 100:
        #     continue

        first = True
        for pixel, group in df_sp.groupby('pixel'):
            group = (group
                     .set_index('t_cpu')
                     # .resample("387S").mean()
                     )

            if first:
                x = group.index.values
                y = group['amplitude'].values
                ysp = group['amplitude_sp'].values
                p_amplitude.plot(x, y, color, label)
                p_amplitudesp.plot(x, ysp, color, label)
                first = False
            else:
                x = group.index.values
                y = group['amplitude'].values
                p_amplitude.plot(x, y, color)

    p_amplitude.save(os.path.join(output_dir, "amplitude.pdf"))
    p_amplitudesp.ax.axhline(60, color='black')
    p_amplitudesp.save(os.path.join(output_dir, "amplitude_sp.pdf"))


def process_file(file):
    name = file.__class__.__name__
    amplitude_path = get_data("d190117_trigger_stability/{}/amplitudes.h5".format(name))
    output_dir = get_plot("d190117_trigger_stability/plot_amplitude/{}".format(name))
    spoi = file.spoi
    process(amplitude_path, output_dir, spoi)


def main():
    files = [
        # d190111(),
        # d190118(),
        d190121(),
    ]
    [process_file(file) for file in files]


if __name__ == '__main__':
    main()
