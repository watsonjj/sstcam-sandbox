from CHECLabPy.plotting.setup import Plotter
from CHECLabPySB import get_plot
from CHECLabPy.core.io import HDF5Reader
from glob import glob
import numpy as np


class Hist(Plotter):
    def plot(self, values, label):
        values = np.rad2deg(values)
        self.ax.hist(values, bins=100, label=label, alpha=0.5)


def main():
    path_gamma = "/Users/Jason/Downloads/tempdata/alpha/mc/gamma_1deg.h5"
    path_proton = "/Users/Jason/Downloads/tempdata/alpha/mc/proton.h5"

    with HDF5Reader(path_gamma) as reader:
        df_gamma = reader.read('source')

    with HDF5Reader(path_proton) as reader:
        df_proton = reader.read('source')

    p_hist = Hist()
    p_hist.plot(df_gamma['alpha90'].values, "Gamma")
    p_hist.plot(df_proton['alpha90'].values, "CRs")
    p_hist.ax.set_xlabel("Alpha (deg)")
    p_hist.ax.set_ylabel("N Events")
    p_hist.add_legend('best')
    p_hist.save(get_plot("d190717_alpha/mc_alpha.pdf"))


if __name__ == '__main__':
    main()
