from CHECLabPy.plotting.setup import Plotter
from CHECLabPySB import get_plot
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
        self.ax.hist2d(x, y, bins=(100, 100))#, norm=LogNorm())


def main():
    path = "/Volumes/gct-jason/astri_onsky_archive/d2019-05-15_simulations/proton.h5"
    output = get_plot("d190524_time_gradient/correlations/mc")

    with HDF5Reader(path) as reader:
        df = reader.read("data")
        df_mc = reader.read("mc")

    tgradient_mc = df['tgradient'].values
    length_mc = df['length'].values
    core_x = df_mc['core_x'].values
    core_y = df_mc['core_y'].values
    impact = np.sqrt(core_x**2 + core_y**2)

    p = Hist2D("Time Gradient (ns/degree)", "Length (degree)")
    p.plot(tgradient_mc, length_mc)
    p.save(join(output, "tgradvslength.pdf"))

    p = Hist2D("Time Gradient (ns/degree)", "Impact Distance (m)")
    mask = np.logical_and(tgradient_mc < 20, tgradient_mc > -20)
    p.plot(tgradient_mc[mask], impact[mask])
    p.save(join(output, "tgradvsimpact.pdf"))

    p = Hist2D("Time Gradient (ns/degree)", "Impact X (m)")
    p.plot(tgradient_mc, core_x)
    p.save(join(output, "tgradvsimpactx.pdf"))

    p = Hist2D("Time Gradient (ns/degree)", "Impact Y (m)")
    p.plot(tgradient_mc, core_y)
    p.save(join(output, "tgradvsimpacty.pdf"))

    p = Hist2D("Impact X (m)", "Impact Y (m)")
    p.plot(core_x, core_y)
    p.save(join(output, "xy.pdf"))

    p = Hist2D("Length (degree)", "Impact Distance (m)")
    p.plot(length_mc, impact)
    p.save(join(output, "lengthvsimpact.pdf"))


if __name__ == '__main__':
    main()
