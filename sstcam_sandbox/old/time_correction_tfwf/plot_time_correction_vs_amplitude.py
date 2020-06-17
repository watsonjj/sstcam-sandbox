import os
import warnings
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import matplotlib.cm as cm
from CHECLabPy.plotting.setup import Plotter
from CHECLabPy.plotting.camera import CameraPlotter
from IPython import embed


class Scatter(Plotter):
    def __init__(self, title="", x_label="", y_label=""):
        super().__init__()
        self.title = title
        self.x_label = x_label
        self.y_label = y_label

    def add(self, x, data, label="", color=None):
        self.ax.plot(x, data, label=label, color=color)

    def add_saturation_region(self, x1, x2):
        self.ax.axvspan(x1, x2, color='red', alpha=0.5, ec=None)

    def finish(self):
        # self.ax.set_title(self.title)
        self.ax.set_xlabel(self.x_label)
        self.ax.set_ylabel(self.y_label)


def main():
    store = pd.HDFStore("/Volumes/gct-jason/data_checs/tf/charge_res_0_peakamp/time_correction_vs_amp.h5")

    mapping = store['mapping']
    with warnings.catch_warnings():
        warnings.simplefilter('ignore', UserWarning)
        mapping.metadata = store.get_storer('mapping').attrs.metadata

    df_all = store['t_correction']

    df = df_all.loc[(df_all['amplitude'] > 200) & (df_all['amplitude'] < 1300)]

    df_acc = df.groupby('pixel').sum().reset_index()
    sum_ = df_acc['sum'].values
    sum2 = df_acc['sum2'].values
    n = df_acc['n'].values
    mean = sum_ / n
    std = np.sqrt((sum2 / n) - (mean ** 2))
    df_acc['t_correction'] = mean
    df_acc['t_correction_std'] = std

    n_pixels = np.unique(df['pixel']).size

    output_dir = "/Volumes/gct-jason/data_checs/tf/time_correction_plots"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print("Created directory: {}".format(output_dir))

    p_amplitude = Scatter("Time Correction vs. Amplitude", "Input Amplitude (mV)", "Time Correction (ns)")
    x = np.unique(df['amplitude'])
    y = df['t_correction'].values.reshape((n_pixels, x.size))
    for p in range(n_pixels):
        p_amplitude.add(x, y[p])
    p_amplitude.save(os.path.join(output_dir, "amplitude.pdf"))

    p_amplitude_channel = Scatter("Time Correction vs. Amplitude", "Input Amplitude (mV)", "Time Correction (ns)")
    x = np.unique(df['amplitude'])
    y = df['t_correction'].values.reshape((n_pixels, x.size))
    c_list = plt.rcParams['axes.prop_cycle'].by_key()['color']
    for p in range(n_pixels):
        channel = p % 16
        color = c_list[channel % len(c_list)]
        p_amplitude_channel.add(x, y[p], "", color)
    p_amplitude_channel.save(os.path.join(output_dir, "amplitude_channel.pdf"))

    p_amplitude_asic = Scatter("Time Correction vs. Amplitude", "Input Amplitude (mV)", "Time Correction (ns)")
    x = np.unique(df['amplitude'])
    y = df['t_correction'].values.reshape((n_pixels, x.size))
    c_list = plt.rcParams['axes.prop_cycle'].by_key()['color']
    for p in range(n_pixels):
        asic = p // 16
        print(asic)
        color = c_list[asic % len(c_list)]
        p_amplitude_asic.add(x, y[p], "", color)
    p_amplitude_asic.save(os.path.join(output_dir, "amplitude_asic.pdf"))

    p_camera = CameraPlotter(mapping)
    image = df_acc['t_correction'].values
    p_camera.plot(image)
    p_camera.colorbar.set_label("Time Correction (ns)")
    p_camera.save(os.path.join(output_dir, "camera.pdf"))

    p_camera_std = CameraPlotter(mapping)
    image = df_acc['t_correction_std'].values
    p_camera_std.plot(image)
    p_camera.colorbar.set_label("Time Correction Standard Deviation (ns)")
    p_camera_std.save(os.path.join(output_dir, "camera_std.pdf"))



if __name__ == '__main__':
    main()