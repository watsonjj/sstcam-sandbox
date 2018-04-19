import os
import pandas as pd
from matplotlib.ticker import FuncFormatter
from CHECLabPy.plotting.setup import Plotter


class RMSEPlotter(Plotter):
    def __init__(self, title=""):
        super().__init__()
        self.title = title

    def add(self, df, label=""):
        true = df['true'].values
        rmse = df['rmse'].values

        self.ax.plot(true, rmse, label=label)

    def finish(self):
        # self.ax.set_title(self.title)
        self.ax.set_xlabel("True Amplitude (mV)")
        self.ax.set_ylabel("RMSE / True")
        self.ax.set_xscale('log')
        self.ax.get_xaxis().set_major_formatter(
            FuncFormatter(lambda x, _: '{:g}'.format(x)))
        self.ax.set_yscale('log')
        self.ax.get_yaxis().set_major_formatter(
            FuncFormatter(lambda y, _: '{:g}'.format(y)))
        # self.ax.set_ylim(0.004, 1)


class CameraPixelCompRMSEPlotter(Plotter):
    def plot(self, df_camera, df_pixel):
        min_ = df_pixel.groupby('true').min()['rmse'].values
        max_ = df_pixel.groupby('true').max()['rmse'].values
        camera = df_camera['rmse'].values
        true = df_camera['true'].values

        self.ax.fill_between(true, min_, max_,
                             color='black', label='Pixel Range')
        self.ax.plot(true, camera, color='blue', label='Camera')

    def finish(self):
        self.ax.set_title("RMSE of Pixels vs Entire Camera")
        self.ax.set_xlabel("True Amplitude (mV)")
        self.ax.set_ylabel("RMSE / True")
        self.ax.set_xscale('log')
        self.ax.get_xaxis().set_major_formatter(
            FuncFormatter(lambda x, _: '{:g}'.format(x)))
        self.ax.set_yscale('log')
        self.ax.get_yaxis().set_major_formatter(
            FuncFormatter(lambda y, _: '{:g}'.format(y)))


def main():
    path_cr_0 = "/Volumes/gct-jason/data_checs/tf/charge_res_0_peakamp/charge_res_0_peakamp.h5"
    path_cr_1 = "/Volumes/gct-jason/data_checs/tf/charge_res_1_lei/charge_resolution_1_lei.h5"
    path_cr_2 = "/Volumes/gct-jason/data_checs/tf/charge_res_2_newref/charge_resolution_2_newref.h5"
    path_cr_3 = "/Volumes/gct-jason/data_checs/tf/charge_res_3_multiref/charge_resolution_3_multiref.h5"
    path_cr_4 = "/Volumes/gct-jason/data_checs/tf/charge_res_4_tfref_600mV/charge_resolution_4_tfref_600mV.h5"
    path_cr_5 = "/Volumes/gct-jason/data_checs/tf/charge_res_5_tfref_6mV/charge_resolution_5_tfref_6mV.h5"
    path_cr_6 = ""
    path_cr_7 = ""

    label_cr_0 = "Peak Amplitude"
    label_cr_1 = "Original Reference Pulse"
    label_cr_2 = "Updated Reference Pulse"
    label_cr_3 = "Reference Pulse Per Amplitude"
    label_cr_4 = "Single TF-WF Reference Pulse (600mV)"
    label_cr_5 = "Single TF-WF Reference Pulse (6mV)"
    label_cr_6 = "Time Correction"
    label_cr_7 = "Time Correction - 1 ns shift"
    label_cr_8 = "Multi-reference Cross-Correlation"

    store_cr_0 = pd.HDFStore(path_cr_0)
    store_cr_1 = pd.HDFStore(path_cr_1)
    store_cr_2 = pd.HDFStore(path_cr_2)
    store_cr_3 = pd.HDFStore(path_cr_3)
    store_cr_4 = pd.HDFStore(path_cr_4)
    store_cr_5 = pd.HDFStore(path_cr_5)
    # store_cr_6 = pd.HDFStore(path_cr_6)
    # store_cr_7 = pd.HDFStore(path_cr_7)
    # store_cr_8 = pd.HDFStore(path_cr_8)

    df_cr_0 = store_cr_0['charge_resolution_camera']
    df_cr_1 = store_cr_1['charge_resolution_camera']
    df_cr_2 = store_cr_2['charge_resolution_camera']
    df_cr_3 = store_cr_3['charge_resolution_camera']
    df_cr_4 = store_cr_4['charge_resolution_camera']
    df_cr_5 = store_cr_5['charge_resolution_camera']
    # df_cr_6 = store_cr_6['charge_resolution_camera']
    # df_cr_7 = store_cr_7['charge_resolution_camera']
    # df_cr_8 = store_cr_8['charge_resolution_camera']

    df_p_cr_1 = store_cr_1['charge_resolution_pixel']

    output_dir = "/Volumes/gct-jason/data_checs/tf/charge_res_plots"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print("Created directory: {}".format(output_dir))

    p_camera_pixel = CameraPixelCompRMSEPlotter()
    p_camera_pixel.plot(df_cr_1, df_p_cr_1)
    p_camera_pixel.add_legend()
    p_camera_pixel.save(os.path.join(output_dir, "camera_pixel_comp.pdf"))

    p_rmse_1 = RMSEPlotter("All")
    # p_rmse_1.add(df_cr_0, label_cr_0)
    p_rmse_1.add(df_cr_1, label_cr_1)
    p_rmse_1.add(df_cr_2, label_cr_2)
    p_rmse_1.add(df_cr_3, label_cr_3)
    p_rmse_1.add(df_cr_4, label_cr_4)
    p_rmse_1.add(df_cr_5, label_cr_5)
    # p_rmse_1.add(df_cr_6, label_cr_6)
    # p_rmse_1.add(df_cr_7, label_cr_7)
    p_rmse_1.add_legend()
    p_rmse_1.save(os.path.join(output_dir, "rmse_all.pdf"))

    p_rmse_2 = RMSEPlotter("All")
    p_rmse_2.add(df_cr_1, label_cr_1)
    p_rmse_2.add(df_cr_3, label_cr_3)
    # p_rmse_2.add(df_cr_4, label_cr_4)
    # p_rmse_2.add(df_cr_5, label_cr_5)
    p_rmse_2.add_legend()
    p_rmse_2.save(os.path.join(output_dir, "rmse_2.pdf"))


if __name__ == '__main__':
    main()
