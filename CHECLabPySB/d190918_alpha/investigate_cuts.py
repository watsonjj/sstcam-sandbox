from CHECLabPy.plotting.setup import Plotter
from CHECLabPy.core.io import HDF5Reader
from CHECLabPySB import get_data, get_plot
from CHECLabPySB.d190918_alpha import *
import numpy as np
import pandas as pd
from matplotlib.colors import LogNorm
from numpy.polynomial.polynomial import polyfit
from os.path import join
from IPython import embed


class Hist(Plotter):
    def plot(self, hist, edges):
        between = (edges[1:] + edges[:-1]) * 0.5
        self.ax.hist(between, weights=hist, bins=edges, histtype='step')


class Hist2D(Plotter):
    def plot(self, hist, xedges, yedges):
        between_x = (xedges[1:] + xedges[:-1]) * 0.5
        between_y = (yedges[1:] + yedges[:-1]) * 0.5
        self.ax.hist2d(
            between_x, between_y, weights=hist, bins=[xedges, yedges]
        )


def plot_hist(values_gamma, values_proton, bins, xlabel, output_path):
    hist_gamma, edges = np.histogram(values_gamma, bins=bins, density=True)
    hist_proton, _ = np.histogram(values_proton, bins=edges, density=True)

    excess = hist_gamma - hist_proton
    between = (edges[1:] + edges[:-1]) * 0.5

    p_hist = Hist()
    p_hist.ax.hist(
        between, weights=hist_gamma, bins=edges,
        histtype='step', label="Gamma"
    )
    p_hist.ax.hist(
        between, weights=hist_proton, bins=edges,
        histtype='step', label="Proton"
    )
    p_hist.ax.set_xlabel(xlabel)
    p_hist.add_legend('best')
    p_hist.ax.set_yscale("log")
    p_hist.save(output_path)


def plot_hist_2d(values_x, values_y, bins_x, bins_y, xlabel, ylabel, output):
    p_hist = Hist2D()
    _, _, _, image = p_hist.ax.hist2d(
        values_x, values_y, bins=[bins_x, bins_y], norm=LogNorm()
    )
    p_hist.fig.colorbar(image)
    p_hist.save(output)


def process(path, output_dir):
    with HDF5Reader(path) as reader:
        df = reader.read("on")
        print(df.columns)

    df_gamma = df.loc[df['diffuse'] == 0]
    df_proton = df.loc[df['diffuse'] == 1]
    n_gamma = df_gamma.index.size
    n_proton = df_proton.index.size

    # cuts = CUTS_ONOFF_SOFT
    # cuts = CUTS_ONOFF_HARSH
    # cuts = CUTS_WOBBLE
    # df = df.query(cuts)

    df_gamma = df.loc[df['diffuse'] == 0]
    df_proton = df.loc[df['diffuse'] == 1]
    n_gamma_ac = df_gamma.index.size
    n_proton_ac = df_proton.index.size

    print(f"Gamma: {n_gamma_ac/n_gamma:.4f}, Proton: {n_proton_ac/n_proton:.4f}")


    # plot_hist_2d(
    #     df_proton['alpha0'].values, df_proton['alpha1'].values,
    #     bins_x=100, bins_y=1000, xlabel=None, ylabel=None,
    #     output=join(output_dir, "alpha0_vs_leakage1i.pdf")
    # )

    plot_hist(
        df_gamma['width'].values, df_proton['width'].values,
        bins=100, xlabel="Width (deg)",
        output_path=join(output_dir, "width.pdf")
    )
    plot_hist(
        df_gamma['length'].values, df_proton['length'].values,
        bins=100, xlabel="Length (deg)",
        output_path=join(output_dir, "length.pdf")
    )
    plot_hist(
        df_gamma['skewness'].values, df_proton['skewness'].values,
        bins=100, xlabel="Skewness",
        output_path=join(output_dir, "skewness.pdf")
    )
    plot_hist(
        df_gamma['kurtosis'].values, df_proton['kurtosis'].values,
        bins=100, xlabel="Kurtosis",
        output_path=join(output_dir, "kurtosis.pdf")
    )
    plot_hist(
        df_gamma['alpha'].values, df_proton['alpha'].values,
        bins=100, xlabel="Alpha",
        output_path=join(output_dir, "alpha.pdf")
    )
    plot_hist(
        df_gamma['leakage1_pixel'].values, df_proton['leakage1_pixel'].values,
        bins=100, xlabel="Leakage1 Pixel",
        output_path=join(output_dir, "leakage1_pixel.pdf")
    )
    plot_hist(
        df_gamma['leakage2_pixel'].values, df_proton['leakage2_pixel'].values,
        bins=100, xlabel="Leakage2 Pixel",
        output_path=join(output_dir, "leakage2_pixel.pdf")
    )
    plot_hist(
        df_gamma['leakage1_intensity'].values, df_proton['leakage1_intensity'].values,
        bins=100, xlabel="Leakage1 Intensity",
        output_path=join(output_dir, "leakage1_intensity.pdf")
    )
    plot_hist(
        df_gamma['leakage2_intensity'].values, df_proton['leakage2_intensity'].values,
        bins=100, xlabel="Leakage2 Intensity",
        output_path=join(output_dir, "leakage2_intensity.pdf")
    )
    plot_hist(
        df_gamma['r'].values, df_proton['r'].values,
        bins=100, xlabel="R",
        output_path=join(output_dir, "r.pdf")
    )
    plot_hist(
        df_gamma['psi'].values, df_proton['psi'].values,
        bins=100, xlabel="psi",
        output_path=join(output_dir, "psi.pdf")
    )
    plot_hist(
        df_gamma['phi'].values, df_proton['phi'].values,
        bins=100, xlabel="phi",
        output_path=join(output_dir, "phi.pdf")
    )
    plot_hist(
        df_gamma['tgradient'].values, df_proton['tgradient'].values,
        bins=100, xlabel="Time Gradient",
        output_path=join(output_dir, "tgradient.pdf")
    )
    plot_hist(
        df_gamma['tduration'].values, df_proton['tduration'].values,
        bins=100, xlabel="Time Duration",
        output_path=join(output_dir, "tduration.pdf")
    )
    plot_hist(
        df_gamma['tdeviation'].values, df_proton['tdeviation'].values,
        bins=100, xlabel="Time Deviation",
        output_path=join(output_dir, "tdeviation.pdf")
    )
    plot_hist(
        df_gamma['tgradient_error'].values, df_proton['tgradient_error'].values,
        bins=100, xlabel="Time Gradient Error",
        output_path=join(output_dir, "tgradient_error.pdf")
    )
    plot_hist(
        df_gamma['width'].values*df_gamma['length'].values/np.log(df_gamma['intensity'].values),
        df_proton['width'].values*df_proton['length'].values/np.log(df_proton['intensity'].values),
        bins=100, xlabel="Width * Length / log(Intensity)",
        output_path=join(output_dir, "wli.pdf")
    )

def main():
    path = get_data("d190918_alpha/extract_alpha_mc/d2019-10-03_simulations_gamma1deg_onoff.h5")
    output_dir = get_plot("d190918_alpha/alpha_mc/cuts")
    process(path, output_dir)


if __name__ == '__main__':
    main()
