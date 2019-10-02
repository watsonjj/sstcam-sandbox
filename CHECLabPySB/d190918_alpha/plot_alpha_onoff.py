from CHECLabPy.plotting.setup import Plotter
from CHECLabPy.core.io import HDF5Reader
from CHECLabPySB import get_data, get_plot
from CHECLabPySB.d190918_alpha import *
import numpy as np
import pandas as pd
from numpy.polynomial.polynomial import polyfit
from os.path import join
from astropy import units as u
from IPython import embed


def li_ma(n_on, n_off, alpha):
    return np.sqrt(2) * np.sqrt(
        n_on * np.log(
            ((1+alpha)/alpha) * (n_on/(n_on+n_off))
        ) +
        n_off * np.log(
            (1+alpha) * (n_off/(n_on+n_off))
        )
    )


def calculate_rates(alpha, weights, bins):
    rate, edges = np.histogram(alpha, weights=weights, bins=bins)
    counts, _ = np.histogram(alpha, bins=edges)
    rate_err = (rate / counts) * np.sqrt(counts)
    return rate, rate_err, edges


class Hist(Plotter):
    def plot(self, rate, rate_err, edges, label):
        between = (edges[1:] + edges[:-1]) * 0.5
        l = self.ax.errorbar(
            between, rate, yerr=rate_err, xerr=np.diff(edges) * 0.5,
            linestyle='', capsize=1, elinewidth=0.5, label=label
        )
        for cap in l[1]:
            cap.set_markeredgewidth(0.5)

    def annotate_region(self, region_size):
        self.ax.axvline(region_size, color='orange', lw=0.5)

    def annotate_li_ma(self, sig_per_sqrthour, rate_on, rate_off, cut, alpha):
        n_hours = (5/sig_per_sqrthour)**2
        print(n_hours)
        self.ax.text(
            0.95, 0.05,
            r"$\sigma_{{Li&Ma}}$ = "f"{sig_per_sqrthour:.2f} "
            r"$\sigma/\sqrt{h}$""\n"
            r"($5\sigma$"f" @ {n_hours:.2f} hours)\n"
            r"$R_{on}$ = "f"{rate_on} events/s\n"
            r"$R_{off}$ = "f"{rate_off} events/s\n"
            r"Cut = "f"{cut:.2f} deg\n"
            r"$\alpha$ = "f"{alpha:.2f}",
            transform=self.ax.transAxes,
            horizontalalignment='right',
            verticalalignment='bottom',
            bbox=dict(
                boxstyle="round", fc='blue', alpha=0.7
            )
        )

    def finish(self):
        self.ax.set_xlabel("Alpha (deg)")
        self.ax.set_ylabel("Events/sec")


class SigVsTime(Plotter):
    def plot(self, time, significance):
        self.ax.plot(np.sqrt(time), significance)


def plot_on_off(alpha_on, alpha_off, weights_on, weights_off,
                alpha_li_ma, region_size, title, output_path):
    time = np.linspace(1, 2*24*60*60, 1000)
    bins = np.linspace(0, 90, 10)

    rate_on_bins, rate_on_err_bins, edges_on = calculate_rates(
        alpha_on, weights_on, bins
    )
    mask_on = alpha_on <= region_size
    rate_on, rate_on_err, _ = calculate_rates(
        alpha_on[mask_on], weights_on[mask_on], 1
    )
    rate_on = rate_on.sum()
    rate_on_err = rate_on_err.sum()
    n_on = rate_on * time

    rate_off_bins, rate_off_err_bins, edges_off = calculate_rates(
        alpha_off, weights_off, bins
    )
    mask_off = alpha_off <= region_size
    rate_off, rate_off_err, _ = calculate_rates(
        alpha_off[mask_off], weights_off[mask_off], 1
    )
    rate_off = rate_off.sum()
    rate_off_err = rate_off_err.sum()
    n_off = rate_off * time

    significance = li_ma(n_on, n_off, alpha_li_ma)
    _, sig_per_sqrthour = polyfit(np.sqrt(time/3600), significance, [1])

    p_hist = Hist()
    p_hist.plot(rate_off_bins, rate_off_err_bins, edges_off, "OFF")
    p_hist.plot(rate_on_bins, rate_on_err_bins, edges_on, "ON")
    p_hist.annotate_region(region_size)
    p_hist.annotate_li_ma(
        sig_per_sqrthour,
        f"{rate_on:.2f}±{rate_on_err:.2f}",
        f"{rate_off:.2f}±{rate_off_err:.2f}",
        region_size,
        alpha_li_ma
    )
    p_hist.ax.set_title(title)
    p_hist.add_legend(1)
    p_hist.save(output_path)


def process(path, output, title, cuts):
    with HDF5Reader(path) as reader:
        df_on = reader.read("on")
        df_off = reader.read("off")
        metadata = reader.get_metadata()
        alpha_li_ma = metadata['alpha_li_ma']
        # cuts = #TODO:
        region_size = 10 # TODO

    if cuts is not None:
        df_on = df_on.query(cuts)
        df_off = df_off.query(cuts)

    time = np.linspace(1, 2*24*60*60, 1000)
    bins = np.linspace(0, 90, 91)

    alpha_on = df_on['alpha'].values
    weights_on = df_on['weights'].values
    rate_on_bins, rate_on_err_bins, edges_on = calculate_rates(
        alpha_on, weights_on, bins
    )
    mask_on = alpha_on <= region_size
    rate_on, rate_on_err, _ = calculate_rates(
        alpha_on[mask_on], weights_on[mask_on], 1
    )
    rate_on = rate_on.sum()
    rate_on_err = rate_on_err.sum()
    n_on = rate_on * time

    alpha_off = df_off['alpha'].values
    weights_off = df_off['weights'].values
    rate_off_bins, rate_off_err_bins, edges_off = calculate_rates(
        alpha_off, weights_off, bins
    )
    mask_off = alpha_off <= region_size
    rate_off, rate_off_err, _ = calculate_rates(
        alpha_off[mask_off], weights_off[mask_off], 1
    )
    rate_off = rate_off.sum()
    rate_off_err = rate_off_err.sum()
    n_off = rate_off * time

    significance = li_ma(n_on, n_off, alpha_li_ma)
    _, sig_per_sqrthour = polyfit(np.sqrt(time/3600), significance, [1])

    p_hist = Hist()
    p_hist.plot(rate_off_bins, rate_off_err_bins, edges_off, "OFF")
    p_hist.plot(rate_on_bins, rate_on_err_bins, edges_on, "ON")
    p_hist.annotate_region(region_size)
    p_hist.annotate_li_ma(
        sig_per_sqrthour,
        f"{rate_on:.2f}±{rate_on_err:.2f}",
        f"{rate_off:.2f}±{rate_off_err:.2f}",
        region_size,
        alpha_li_ma
    )
    p_hist.ax.set_title(title)
    p_hist.add_legend(1)
    p_hist.save(output)


    # # Cuts for "ghost" events
    # df = df.loc[
    #     (df['baseline_mean'] < 11.88)
    #     & (df['charge_median'] < 11)
    #     & (df['size_tm_20'] < 24.5)
    #     & (df['size_tm_40'] < 14.5)
    # ]



    #
    #     & (df['tduration'] < 25)
    #     # & (df['leakage2_intensity'] < 0.1)
    #     # & (df['width'] < 0.2)
    #     # & (df['length'] < 0.9)
    #     # & (df['width'] * df['length'] / np.log(df['intensity']) < 0.015),
    # ]

    # TODO:
    # df = df.loc[df['diffuse'] == 0]
    # alpha0 = df['alpha0'].values
    # alpha1 = df['alpha1'].values
    # df['alpha0'] = alpha1
    # df['alpha1'] = alpha0

    # df_wobble = df
    # # df_wobble = df.loc[
    # #     (df['tduration'] < 25)
    # # ]
    # alpha_on = df_wobble['alpha0'].values
    # weights_on = df_wobble['weights'].values
    # alpha_off = np.concatenate([
    #     df_wobble[f'alpha{i}'] for i in range(1, n_onoff)
    # ])
    # weights_off = np.concatenate([
    #     df_wobble['weights'] for i in range(1, n_onoff)
    # ])
    # region_size = 10
    # plot_on_off(
    #     alpha_on, alpha_off, weights_on, weights_off, 1/(n_onoff-1),
    #     region_size, "Wobble MC", join(output_dir, "hist_wobble.pdf")
    # )
    #
    # df_onoff = df
    # # df_onoff = df.loc[
    # #     (df['tduration'] < 25)
    # #     & (df['leakage2_intensity'] < 0.1)
    # #     & (df['width'] < 0.2)
    # #     & (df['length'] < 0.9)
    # #     & (df['width'] * df['length'] / np.log(df['intensity']) < 0.015),
    # # ]
    # df_gamma = df_onoff.loc[df_onoff['diffuse'] == 0]
    # df_proton = df_onoff.loc[df_onoff['diffuse'] == 1]
    # df_on = pd.concat([df_gamma, df_proton])
    # df_off = df_proton
    # alpha_on = df_on['alpha0'].values
    # weights_on = df_on['weights'].values
    # alpha_off = df_off['alpha0'].values
    # weights_off = df_off['weights'].values
    # region_size = 10
    # plot_on_off(
    #     alpha_on, alpha_off, weights_on, weights_off, 1,
    #     region_size, "ON/OFF MC", join(output_dir, "hist_onoff.pdf")
    # )

def main():
    path = get_data("d190918_alpha/d2019-05-15_simulations_gamma1deg_onoff.h5")
    output = get_plot("d190918_alpha/d2019-05-15_simulations_gamma1deg_onoff_nocut.pdf")
    title = "ON/OFF MC (1deg) (No cuts)"
    process(path, output, title, None)
    output = get_plot("d190918_alpha/d2019-05-15_simulations_gamma1deg_onoff_softcut.pdf")
    title = "ON/OFF MC (1deg) (Soft cuts)"
    process(path, output, title, cuts_onoff_soft)
    output = get_plot("d190918_alpha/d2019-05-15_simulations_gamma1deg_onoff_harshcut.pdf")
    title = "ON/OFF MC (1deg) (Harsh cuts)"
    process(path, output, title, cuts_onoff_harsh)

    path = get_data("d190918_alpha/d2019-05-15_simulations_gamma1deg_wobble.h5")
    output = get_plot("d190918_alpha/d2019-05-15_simulations_gamma1deg_wobble_nocut.pdf")
    title = "Wobble MC (1deg) (No cuts)"
    process(path, output, title, None)
    output = get_plot("d190918_alpha/d2019-05-15_simulations_gamma1deg_wobble_cut.pdf")
    title = "Wobble MC (1deg)"
    process(path, output, title, cuts_wobble)

    path = get_data("d190918_alpha/d2019-05-15_simulations_gammaonly_wobble.h5")
    output = get_plot("d190918_alpha/d2019-05-15_simulations_gammaonly_wobble_nocut.pdf")
    title = "Wobble MC (1deg) (No cuts)"
    process(path, output, title, None)
    output = get_plot("d190918_alpha/d2019-05-15_simulations_gammaonly_wobble_cut.pdf")
    title = "Wobble MC (1deg)"
    process(path, output, title, cuts_wobble)


if __name__ == '__main__':
    main()
