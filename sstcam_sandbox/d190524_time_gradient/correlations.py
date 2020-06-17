from CHECLabPy.plotting.setup import Plotter
from sstcam_sandbox import get_plot
from CHECLabPy.core.io import HDF5Reader
from os.path import join
import numpy as np
from matplotlib.colors import LogNorm
from IPython import embed


class Hist2D(Plotter):
    def __init__(self, xlabel, ylabel):
        super().__init__()
        self.ax.set_xlabel(xlabel)
        self.ax.set_ylabel(ylabel)

    def plot(self, x, y):
        self.ax.hist2d(x, y, bins=(100, 100), norm=LogNorm())


def main():
    path = "/Volumes/gct-jason/astri_onsky_archive/hillas_over_campaign.h5"
    output = get_plot("d190524_time_gradient/correlations/data")

    with HDF5Reader(path) as reader:
        df = reader.read("data")

    tgradient = df['tgradient'].values
    length = df['length'].values
    width = df['width'].values

    notnoisy = ~np.logical_and(length > 0.1, width > 0.1)
    tgradient = tgradient[notnoisy]
    length = length[notnoisy]
    width = width[notnoisy]

    p = Hist2D("Time Gradient (ns/degree)", "Length (degree)")
    p.plot(tgradient, length)
    p.save(join(output, "tgradvslength.pdf"))


if __name__ == '__main__':
    main()
