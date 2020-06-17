from sstcam_sandbox import get_data, get_plot
from TargetCalibSB.tf import TFDC
from TargetCalibSB.vped import VpedCalibrator
from CHECLabPy.plotting.setup import Plotter


class TFPlot(Plotter):
    def plot(self, x, y, label=None):
        self.ax.plot(x, y, label=label)


def get_dc_tf(dc_tf_path, vped_calibration_path):
    tf = TFDC.from_file(dc_tf_path)
    vped_calibrator = VpedCalibrator()
    vped_calibrator.load(vped_calibration_path)
    tf.finish_generation(vped_calibrator)
    return tf


def get_ac_tf(ac_tf_path):
    tf = TFDC.from_tcal(ac_tf_path)
    # tf.finish_generation()
    return tf


def plot_comparison(tfs, channel, cell, title, output_path):
    p_tf = TFPlot()
    for label, tf in tfs.items():
        p_tf.plot(
            tf._input_amplitudes,
            tf.tf[channel, cell],
            label
        )
    p_tf.ax.set_xlabel("VPED")
    p_tf.ax.set_ylabel("Pedestal-subtracted ADC")
    p_tf.ax.set_title(title)
    p_tf.add_legend('best')
    p_tf.save(output_path)


def plot_comparison_ref(tfs, channel, cell, title, output_path):
    ref = None
    p_tf = TFPlot()
    for label, tf in tfs.items():
        x = tf._input_amplitudes[:21]
        y = tf.tf[channel, cell][:21]
        if ref is None:
            ref = y
            label = label + " (ref)"
        p_tf.plot(x, y - ref, label=label)
    p_tf.ax.set_xlabel("VPED")
    p_tf.ax.set_ylabel("Difference in ADC from ref")
    p_tf.ax.set_title(title)
    p_tf.add_legend('best')
    p_tf.save(output_path)


def plot_comparison_ref_stat(tfs, title, output_path):
    ref = None
    p_tf = TFPlot()
    for label, tf in tfs.items():
        x = tf._input_amplitudes[:21]
        y = tf.tf[..., :21]
        if ref is None:
            ref = y
            label = label + " (ref)"
        # p_tf.plot(x, y - ref, label=label)
        y_mean = (y - ref).mean((0, 1))
        y_std = (y - ref).std((0, 1))

        (_, caps, _) = p_tf.ax.errorbar(
            x, y_mean, yerr=y_std, mew=1, capsize=1, elinewidth=0.5,
            markersize=2, label=label, linewidth=0.5, fmt='.',
        )
        for cap in caps:
            cap.set_markeredgewidth(0.5)
    p_tf.ax.set_xlabel("VPED")
    p_tf.ax.set_ylabel("Difference in ADC from ref")
    p_tf.ax.set_title(title)
    p_tf.add_legend('best')
    p_tf.save(output_path)


def get_tf(path):
    tf = TFDC.from_file(path)
    tf.finish_generation()
    return tf


def main():
    before_tfs = dict(
        before_25deg=get_tf(get_data("d191128_pedestal_lab/dc_tf/before_25deg.h5")),
        before_35deg=get_tf(get_data("d191128_pedestal_lab/dc_tf/before_35deg.h5")),
    )
    after_tfs = dict(
        c440pF_25deg=get_tf(get_data("d191128_pedestal_lab/dc_tf/after_25deg.h5")),
        c440pF_25deg_2=get_tf(get_data("d191128_pedestal_lab/dc_tf/after_25deg_3.h5")),
        c440pF_35deg=get_tf(get_data("d191128_pedestal_lab/dc_tf/after_35deg.h5")),
        c440pF_35deg_2=get_tf(get_data("d191128_pedestal_lab/dc_tf/after_35deg_3.h5")),
    )
    # after_tfs = dict(
    #     c100pF_25deg=get_tf(get_data("d191128_pedestal_lab/dc_tf/100pF_25deg.h5")),
    #     c100pF_1k_25deg=get_tf(get_data("d191128_pedestal_lab/dc_tf/100pF_1k_25deg.h5")),
    #     c100pF_35deg=get_tf(get_data("d191128_pedestal_lab/dc_tf/100pF_35deg.h5")),
    # )
    # after_tfs = dict(
    #     c200pF_25deg=get_tf(get_data("d191128_pedestal_lab/dc_tf/200pF_25deg.h5")),
    #     c200pF_35deg=get_tf(get_data("d191128_pedestal_lab/dc_tf/200pF_35deg.h5")),
    # )
    channel = 8
    cell = 0
    title = f"BEFORE Capacitor Change, Channel = {channel}, Cell = {cell}"
    output_path = get_plot("d191128_pedestal_lab/dc_tf/before.pdf")
    plot_comparison(before_tfs, channel, cell, title, output_path)
    output_path = get_plot("d191128_pedestal_lab/dc_tf/ref_before.pdf")
    plot_comparison_ref(before_tfs, channel, cell, title, output_path)
    title = f"AFTER Capacitor Change, Channel = {channel}, Cell = {cell}"
    output_path = get_plot("d191128_pedestal_lab/dc_tf/after.pdf")
    plot_comparison(after_tfs, channel, cell, title, output_path)
    output_path = get_plot("d191128_pedestal_lab/dc_tf/ref_after.pdf")
    plot_comparison_ref(after_tfs, channel, cell, title, output_path)
    output_path = get_plot("d191128_pedestal_lab/dc_tf/ref_stat_after.pdf")
    plot_comparison_ref_stat(after_tfs, "", output_path)

    # output_path = get_plot("d191128_pedestal_lab/dc_tf/all.pdf")
    # plot_comparison({**before_tfs, **after_tfs}, channel, cell, "", output_path)
    # output_path = get_plot("d191128_pedestal_lab/dc_tf/ref_all.pdf")
    # plot_comparison_ref({**before_tfs, **after_tfs}, channel, cell, "", output_path)



if __name__ == '__main__':
    main()
