from CHECLabPy.plotting.setup import Plotter
from CHECLabPy.core.io import HDF5Reader
from sstcam_sandbox import get_data, get_plot
from sstcam_sandbox.d190918_alpha import *
from sstcam_sandbox.d190918_alpha.plot_alpha_mc import calculate_rates, li_ma
import numpy as np
from numpy.polynomial.polynomial import polyfit
from IPython import embed


class RegionSizePlotter(Plotter):
    def plot(self, region_sizes, significances):
        self.ax.plot(region_sizes, significances, 'x')
        # caps = self.ax.errorbar(
        #     region_sizes, mean, yerr=std,
        #     fmt='x', linestyle='', capsize=1, elinewidth=0.5
        # )
        # for cap in caps[1]:
        #     cap.set_markeredgewidth(0.5)

        max_ = region_sizes[np.nanargmax(significances)]
        self.ax.set_title(f"max = {max_:.2f} degrees")


def process(path, output, title, cuts):
    with HDF5Reader(path) as reader:
        df_on = reader.read("on")
        df_off = reader.read("off")
        metadata = reader.get_metadata()
        alpha_li_ma = metadata['alpha_li_ma']

    if cuts is not None:
        df_on = df_on.query(cuts)
        df_off = df_off.query(cuts)

    time = 50 * 60 * 60
    region_sizes = np.linspace(0, 20, 200)[1:]
    significances = np.zeros(region_sizes.size)
    std = np.zeros(region_sizes.size)

    for i, region_size in enumerate(region_sizes):
        alpha_on = df_on['alpha'].values
        weights_on = df_on['weights'].values
        mask_on = alpha_on <= region_size
        rate_on_mean, rate_on_std, _ = calculate_rates(
            alpha_on[mask_on], weights_on[mask_on], 1
        )
        rate_on = rate_on_mean.sum()
        n_on = rate_on * time

        alpha_off = df_off['alpha'].values
        weights_off = df_off['weights'].values
        mask_off = alpha_off <= region_size
        rate_off_mean, rate_off_std, _ = calculate_rates(
            alpha_off[mask_off], weights_off[mask_off], 1
        )
        rate_off = rate_off_mean.sum()
        n_off = rate_off * time

        significance = li_ma(n_on, n_off, alpha_li_ma)
        significances[i] = significance

    p_rs = RegionSizePlotter()
    p_rs.plot(region_sizes, significances)
    p_rs.save(output)


def main():
    # path = get_data("d190918_alpha/d2019-05-15_simulations_gamma1deg_onoff.h5")
    # output = get_plot("d190918_alpha/optimise_alpha_cut/d2019-05-15_simulations_gamma1deg_onoff_nocut.pdf")
    # title = "ON/OFF MC (1deg) (No cuts)"
    # process(path, output, title, None)
    # output = get_plot("d190918_alpha/optimise_alpha_cut/d2019-05-15_simulations_gamma1deg_onoff_softcut.pdf")
    # title = "ON/OFF MC (1deg) (Soft cuts)"
    # process(path, output, title, CUTS_ONOFF_SOFT)
    # output = get_plot("d190918_alpha/optimise_alpha_cut/d2019-05-15_simulations_gamma1deg_onoff_harshcut.pdf")
    # title = "ON/OFF MC (1deg) (Harsh cuts)"
    # process(path, output, title, CUTS_ONOFF_HARSH)
    #
    # path = get_data("d190918_alpha/d2019-05-15_simulations_gamma1deg_wobble.h5")
    # output = get_plot("d190918_alpha/optimise_alpha_cut/d2019-05-15_simulations_gamma1deg_wobble_nocut.pdf")
    # title = "Wobble MC (1deg) (No cuts)"
    # process(path, output, title, None)
    # output = get_plot("d190918_alpha/optimise_alpha_cut/d2019-05-15_simulations_gamma1deg_wobble_cut.pdf")
    # title = "Wobble MC (1deg)"
    # process(path, output, title, CUTS_WOBBLE)

    path = get_data("d190918_alpha/extract_alpha_mc/d2019-10-03_simulations_gamma1deg_onoff.h5")
    output = get_plot("d190918_alpha/optimise_alpha_cut/d2019-10-03_simulations_gamma1deg_onoff_nocut.pdf")
    title = "ON/OFF MC (1deg) (No cuts)"
    process(path, output, title, None)
    output = get_plot("d190918_alpha/optimise_alpha_cut/d2019-10-03_simulations_gamma1deg_onoff_softcut.pdf")
    title = "ON/OFF MC (1deg) (Soft cuts)"
    process(path, output, title, CUTS_ONOFF_SOFT)
    output = get_plot("d190918_alpha/optimise_alpha_cut/d2019-10-03_simulations_gamma1deg_onoff_harshcut.pdf")
    title = "ON/OFF MC (1deg) (Harsh cuts)"
    process(path, output, title, CUTS_ONOFF_HARSH)

    path = get_data("d190918_alpha/extract_alpha_mc/d2019-10-03_simulations_gamma1deg_wobble.h5")
    output = get_plot("d190918_alpha/optimise_alpha_cut/d2019-10-03_simulations_gamma1deg_wobble_nocut.pdf")
    title = "Wobble MC (1deg) (No cuts)"
    process(path, output, title, None)
    output = get_plot("d190918_alpha/optimise_alpha_cut/d2019-10-03_simulations_gamma1deg_wobble_cut.pdf")
    title = "Wobble MC (1deg)"
    process(path, output, title, CUTS_WOBBLE)


if __name__ == '__main__':
    main()
