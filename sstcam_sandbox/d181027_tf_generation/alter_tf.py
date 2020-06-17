from sstcam_sandbox.plotting.setup import Plotter
from sstcam_sandbox import get_data, get_plot
from target_calib import TFArrayReader, CalibReadWriter
import numpy as np
import re
from numpy.polynomial.polynomial import polyfit, polyval
from IPython import embed


class TFPlot(Plotter):
    def plot(self, steps, tf):
        self.ax.axhline(18*4)
        self.ax.plot(steps, tf[0, 0, 0], 'x', ms=0.2)
        # embed()
        # self.ax.plot(steps, tf[0, -1].T)


        self.ax.set_xlabel("ADC")
        self.ax.set_ylabel("mV")


def linear(steps, tf):
    # tf[:, :, :] = steps

    thresh_mV = 18 * 4
    tf_linear = steps.copy()
    tf_average = np.mean(tf, (0, 1, 2))

    flag = np.zeros(tf_average.size, dtype=np.bool)
    argsort = np.abs(tf_average - thresh_mV).argsort()
    flag[argsort[:3]] = True

    x = steps[flag]
    y = tf_average[flag]

    p = polyfit(x, y, [1])

    tf[:, :, :] = polyval(steps, p)

    return steps, tf


def average(steps, tf):
    tf[:, :, :] = np.mean(tf, (0, 1, 2))
    return steps, tf


def average_per_pixel(steps, tf):
    n_pixels = tf.shape[1]
    for ipix in range(n_pixels):
        tf[0, ipix, :] = tf[0, ipix].mean(0)
    return steps, tf


def mix(steps, tf):
    thresh_mV = 18 * 4
    tf_linear = steps.copy()
    tf_average = np.mean(tf, (0, 1, 2))

    flag = np.zeros(tf_average.size, dtype=np.bool)
    argsort = np.abs(tf_average - thresh_mV).argsort()
    flag[argsort[:3]] = True

    x = steps[flag]
    y = tf_average[flag]

    p = polyfit(x, y, [1])

    tf_average[:argsort[0]] = polyval(steps[:argsort[0]], p)
    tf[:, :, :] = tf_average
    # embed()

    return steps, tf


def mix2(steps, tf):
    thresh_mV = 18 * 4
    tf_linear = steps.copy()
    tf_average = np.mean(tf, (0, 1, 2))

    thresh_step = np.abs(steps - thresh_mV).argmin()
    shift = steps[thresh_step+1] - tf_average[thresh_step + 1]
    tf_average += shift

    tf_linear[thresh_step:] = tf_average[thresh_step:]

    tf[:, :, :] = tf_linear
    # embed()

    return steps, tf



def process(input_path, function):

    pattern = '(.+)(SN\d{4})(.+)'
    reg_exp = re.search(pattern, input_path)
    sn = reg_exp[2]

    name = function.__name__
    output_path = get_data("d181027_tf_generation/alter_tf/{}_{}.tcal".format(name, sn))
    plot_path = get_plot("d181027_tf_generation/alter_tf/{}_{}.pdf".format(name, sn))

    print("Reading TF: {}".format(input_path))
    reader = TFArrayReader(input_path)
    tf = np.array(reader.GetTF())
    steps = np.array(reader.GetAdcSteps())

    steps, tf = function(steps, tf)

    print("Writing TF: {}".format(output_path))
    rw = CalibReadWriter()
    rw.WriteTfData(output_path, steps.tolist(), tf, True)

    reader = TFArrayReader(output_path)
    tf = np.array(reader.GetTF())
    steps = np.array(reader.GetAdcSteps())

    p_tf = TFPlot()
    p_tf.plot(steps, tf)
    p_tf.save(plot_path)


def main():
    path = "/Users/Jason/Software/CHECDevelopmentOperation/SN0056_tf.tcal"
    process(path, linear)
    process(path, average)
    process(path, average_per_pixel)
    process(path, mix)
    process(path, mix2)


if __name__ == '__main__':
    main()