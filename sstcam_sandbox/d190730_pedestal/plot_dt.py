from CHECLabPy.plotting.setup import Plotter
from sstcam_sandbox.d190730_pedestal import all_files
import numpy as np
from os.path import join


class Hist(Plotter):
    def plot(self, values):
        self.ax.hist(values, bins=100)
        self.ax.set_xlabel("Delta t_cpu (ns)")
        self.ax.set_yscale("log")


def process(input_path, output_dir):
    dt = np.load(input_path)
    dt = dt[dt < 2000000]

    p_hist = Hist()
    p_hist.plot(dt)
    p_hist.save(join(output_dir, "dt.pdf"))


def main():
    for file in all_files:
        process(file.reduced_dt, file.plot_dir)


if __name__ == '__main__':
    main()
