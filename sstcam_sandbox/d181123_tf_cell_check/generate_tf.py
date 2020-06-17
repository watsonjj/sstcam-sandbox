from sstcam_sandbox.plotting.setup import Plotter
from target_calib import TFArrayReader, CalibReadWriter
import numpy as np
from sstcam_sandbox.d181123_tf_cell_check import TF_Sampling, TF_Storage
from IPython import embed


class TFPlot(Plotter):
    def plot(self, steps, tf):
        self.ax.plot(steps, tf[0, 0].T, 'x', ms=0.2)

        self.ax.set_xlabel("ADC")
        self.ax.set_ylabel("mV")


def process(file):
    output_path = file.path
    plot_path = file.plot_path

    n_tm = 1
    n_pixel = 64
    n_cell = file.n_cell
    n_steps = 5

    steps = np.linspace(-350, 3648, n_steps, dtype=np.int64)
    tf = np.zeros((n_tm, n_pixel, n_cell, n_steps))
    for c in range(n_cell):
        tf[:, :, c, :] = c

    print("Writing TF: {}".format(output_path))
    rw = CalibReadWriter()
    rw.WriteTfData(output_path, steps.tolist(), tf, True)

    reader = TFArrayReader(output_path)
    tf = np.array(reader.GetTF())
    steps = np.array(reader.GetAdcSteps())

    p_tf = TFPlot(switch_backend=True)
    p_tf.plot(steps, tf)
    p_tf.save(plot_path)


def main():
    process(TF_Sampling())
    process(TF_Storage())


if __name__ == '__main__':
    main()
