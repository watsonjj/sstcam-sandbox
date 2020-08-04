from sstcam_sandbox import get_data, get_plot
from sstcam_sandbox.d191122_dc_tf import get_dc_tf, get_ac_tf, get_ac_cc_tf
from CHECLabPy.plotting.setup import Plotter
import numpy as np
from numba import guvectorize, float64


class TFPlot(Plotter):
    def plot(self, x, y, label=None):
        self.ax.plot(x, y, label=label)


def plot_single_comparison(tfs, channel, cell, output_path):
    p_tf = TFPlot()
    for label, tf in tfs.items():
        p_tf.plot(
            tf.x[channel, cell],
            tf.tf[channel, cell],
            label
        )
    p_tf.ax.set_xlabel("mV")
    p_tf.ax.set_ylabel("Pedestal-subtracted ADC")
    p_tf.ax.set_title(f"Channel = {channel}, Cell = {cell}")
    p_tf.add_legend('best')
    p_tf.save(output_path)


def plot_channel(tf, channel, title, output_path):
    p_tf = TFPlot()
    p_tf.plot(
        tf.x[channel].T,
        tf.tf[channel].T,
    )
    p_tf.ax.set_xlabel("mV")
    p_tf.ax.set_ylabel("Pedestal-subtracted ADC")
    p_tf.ax.set_title(title)
    p_tf.save(output_path, dpi=600)


def plot_relative(dc_tf, ac_tf, channel, output_path):
    dc_x = dc_tf.x[channel]
    dc_y = dc_tf.tf[channel]

    ac_x = ac_tf.x[channel]
    ac_y = ac_tf.tf[channel]

    @guvectorize(
        [(float64[:], float64[:], float64[:], float64[:])],
        '(d),(a),(a)->(d)',
        nopython=True
    )
    def interp1d(x, xf, yf, y):
        y[:] = np.interp(x, xf, yf)

    ac_y = interp1d(dc_x, ac_x, ac_y)
    ac_x = dc_x

    p_tf = TFPlot()
    p_tf.plot(ac_x.T, (ac_y / dc_y).T)
    p_tf.ax.set_xlabel("mV")
    p_tf.ax.set_ylabel("Relative ADC")
    p_tf.ax.set_title(f"Channel = {channel}")
    # p_tf.add_legend('best')
    p_tf.save(output_path, dpi=600)


def plot_std(tf, channel, cell, output_path):
    p_tf = TFPlot()
    # (_, caps, _) = p_tf.ax.errorbar(
    #     tf.x[channel, cell], tf.tf[channel, cell], yerr=tf.std[channel, cell],
    #     fmt='x', mew=1, markersize=3, capsize=3, elinewidth=0.7
    # )
    # for cap in caps:
    #     cap.set_markeredgewidth(0.7)
    p_tf.plot(tf.x[channel, cell], tf.std[channel, cell])
    p_tf.ax.set_xlabel("mV")
    p_tf.ax.set_ylabel("Pedestal-subtracted ADC")
    p_tf.save(output_path, dpi=600)


def main():
    path_ac_23 = get_data("d191122_dc_tf/ac_tf/TFInput_File_SN0038_temp_23_180317.tcal")
    path_ac_cc_23 = get_data("d191122_dc_tf/ac_tf/ac_23deg_tf.h5")
    path_dc_ext23 = get_data("d191122_dc_tf/dc_tf/dc_externalsync_23deg_tf.tcal")
    path_vped_23 = get_data("d191122_dc_tf/vped/VPED_23deg.h5")

    tf_ac_23 = get_ac_tf(path_ac_23)
    tf_ac_cc_23 = get_ac_cc_tf(path_ac_cc_23)
    tf_dc_ext23 = get_dc_tf(path_dc_ext23, path_vped_23)

    # COMPARISON, SINGLE CHANNEL & CELL
    tfs = dict(
        DC=tf_dc_ext23,
        AC=tf_ac_23,
        AC_CC=tf_ac_cc_23,
    )
    channel = 0
    cell = 0
    output_path = get_plot(f"d191122_dc_tf/plot_tf/single_ch{channel}_c{cell}.pdf")
    plot_single_comparison(tfs, channel, cell, output_path)
    channel = 15
    cell = 0
    output_path = get_plot(f"d191122_dc_tf/plot_tf/single_ch{channel}_c{cell}.pdf")
    plot_single_comparison(tfs, channel, cell, output_path)
    channel = 8
    cell = 0
    output_path = get_plot(f"d191122_dc_tf/plot_tf/single_ch{channel}_c{cell}.pdf")
    plot_single_comparison(tfs, channel, cell, output_path)
    channel = 8
    cell = 31
    output_path = get_plot(f"d191122_dc_tf/plot_tf/single_ch{channel}_c{cell}.pdf")
    plot_single_comparison(tfs, channel, cell, output_path)
    channel = 8
    cell = 16
    output_path = get_plot(f"d191122_dc_tf/plot_tf/single_ch{channel}_c{cell}.pdf")
    plot_single_comparison(tfs, channel, cell, output_path)

    # FULL TFS, SINGLE CHANNEL
    channel = 8
    title = f"DC TF, External Trigger, Temperature 23°C, Channel {channel}"
    output_path = get_plot("d191122_dc_tf/plot_tf/dc_ext23.png")
    plot_channel(tf_dc_ext23, channel, title, output_path)

    title = f"AC TF, Temperature 23°C, Channel {channel}"
    output_path = get_plot("d191122_dc_tf/plot_tf/ac_23.png")
    plot_channel(tf_ac_23, channel, title, output_path)

    # RELATIVE, SINGLE CHANNEL
    channel = 8
    output_path = get_plot(f"d191122_dc_tf/plot_tf/relative_ch{channel}.png")
    plot_relative(tf_dc_ext23, tf_ac_23, channel, output_path)

    # STDDEV
    channel = 8
    cell = 0
    output_path = get_plot(f"d191122_dc_tf/plot_tf/stddev.png")
    plot_std(tf_dc_ext23, channel, cell, output_path)

if __name__ == '__main__':
    main()
