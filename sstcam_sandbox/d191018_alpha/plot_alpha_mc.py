from CHECLabPy.plotting.setup import Plotter
from CHECLabPy.core.io import HDF5Reader
from sstcam_sandbox import get_data, get_plot
from sstcam_sandbox.d191018_alpha import *
import numpy as np
from numpy.polynomial.polynomial import polyfit
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
        color = self.ax._get_lines.get_next_color()
        between = (edges[1:] + edges[:-1]) * 0.5
        self.ax.hist(between, weights=rate, bins=edges, histtype='step', color=color)
        caps = self.ax.errorbar(
            between, rate, yerr=rate_err, xerr=np.diff(edges) * 0.5,
            linestyle='', capsize=1, elinewidth=0.5, label=label, color=color
        )
        for cap in caps[1]:
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


def process(path, output, title, cuts):
    with HDF5Reader(path) as reader:
        df_on = reader.read("on")
        df_off = reader.read("off")
        metadata = reader.get_metadata()
        alpha_li_ma = metadata['alpha_li_ma']

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
    print(f"Total Rate ON: {rate_on_bins.sum()}")
    mask_on = alpha_on <= REGION_SIZE
    rate_on, rate_on_err, _ = calculate_rates(
        alpha_on[mask_on], weights_on[mask_on], 1
    )
    rate_on = rate_on.sum()
    print(f"Alpha Rate ON: {rate_on.sum()}")
    rate_on_err = rate_on_err.sum()
    n_on = rate_on * time

    alpha_off = df_off['alpha'].values
    weights_off = df_off['weights'].values
    rate_off_bins, rate_off_err_bins, edges_off = calculate_rates(
        alpha_off, weights_off, bins
    )
    print(f"Total Rate OFF: {rate_off_bins.sum()}")
    mask_off = alpha_off <= REGION_SIZE
    rate_off, rate_off_err, _ = calculate_rates(
        alpha_off[mask_off], weights_off[mask_off], 1
    )
    rate_off = rate_off.sum()
    print(f"Alpha Rate OFF: {rate_off.sum()}")
    rate_off_err = rate_off_err.sum()
    n_off = rate_off * time

    significance = li_ma(n_on, n_off, alpha_li_ma)
    _, sig_per_sqrthour = polyfit(np.sqrt(time/3600), significance, [1])

    rate_off_bins *= alpha_li_ma
    rate_off_err_bins *= alpha_li_ma

    p_hist = Hist()
    p_hist.plot(rate_off_bins, rate_off_err_bins, edges_off, "OFF")
    p_hist.plot(rate_on_bins, rate_on_err_bins, edges_on, "ON")
    p_hist.annotate_region(REGION_SIZE)
    p_hist.annotate_li_ma(
        sig_per_sqrthour,
        f"{rate_on:.2f}±{rate_on_err:.2f}",
        f"{rate_off:.2f}±{rate_off_err:.2f}",
        REGION_SIZE,
        alpha_li_ma
    )
    p_hist.ax.set_title(title)
    p_hist.add_legend(1)
    p_hist.save(output)


def main():
    path = get_data("d191018_alpha/extract_alpha_mc/d2019-05-15_simulations_gamma0deg_onoff.h5")
    output = get_plot("d191018_alpha/d2019-05-15_simulations/gamma0deg_onoff_nocut.pdf")
    title = "ON/OFF MC (1deg) (No cuts)"
    process(path, output, title, None)
    output = get_plot("d191018_alpha/d2019-05-15_simulations/gamma0deg_onoff_softcut.pdf")
    title = "ON/OFF MC (1deg) (Soft cuts)"
    process(path, output, title, CUTS_ONOFF_SOFT)
    output = get_plot("d191018_alpha/d2019-05-15_simulations/gamma0deg_onoff_harshcut.pdf")
    title = "ON/OFF MC (1deg) (Harsh cuts)"
    process(path, output, title, CUTS_ONOFF_HARSH)

    path = get_data("d191018_alpha/extract_alpha_mc/d2019-05-15_simulations_gamma1deg_onoff.h5")
    output = get_plot("d191018_alpha/d2019-05-15_simulations/gamma1deg_onoff_nocut.pdf")
    title = "ON/OFF MC (1deg) (No cuts)"
    process(path, output, title, None)
    output = get_plot("d191018_alpha/d2019-05-15_simulations/gamma1deg_onoff_softcut.pdf")
    title = "ON/OFF MC (1deg) (Soft cuts)"
    process(path, output, title, CUTS_ONOFF_SOFT)
    output = get_plot("d191018_alpha/d2019-05-15_simulations/gamma1deg_onoff_harshcut.pdf")
    title = "ON/OFF MC (1deg) (Harsh cuts)"
    process(path, output, title, CUTS_ONOFF_HARSH)

    path = get_data("d191018_alpha/extract_alpha_mc/d2019-05-15_simulations_gamma1deg_wobble.h5")
    output = get_plot("d191018_alpha/d2019-05-15_simulations/gamma1deg_wobble_nocut.pdf")
    title = "Wobble MC (1deg) (No cuts)"
    process(path, output, title, None)
    output = get_plot("d191018_alpha/d2019-05-15_simulations/gamma1deg_wobble_cut.pdf")
    title = "Wobble MC (1deg)"
    process(path, output, title, CUTS_WOBBLE)

    path = get_data("d191018_alpha/extract_alpha_mc/d2019-05-15_simulations_gamma1deg_5off_wobble.h5")
    output = get_plot("d191018_alpha/d2019-05-15_simulations/gamma1deg_5off_wobble_nocut.pdf")
    title = "Wobble MC (1deg) (5 OFF) (No cuts)"
    process(path, output, title, None)
    output = get_plot("d191018_alpha/d2019-05-15_simulations/gamma1deg_5off_wobble_cut.pdf")
    title = "Wobble MC (1deg) (5 OFF)"
    process(path, output, title, CUTS_WOBBLE)
    #
    path = get_data("d191018_alpha/extract_alpha_mc/d2019-05-15_simulations_gammaonly_wobble.h5")
    output = get_plot("d191018_alpha/d2019-05-15_simulations/gammaonly_wobble_nocut.pdf")
    title = "Wobble MC (1deg) (No cuts)"
    process(path, output, title, None)
    output = get_plot("d191018_alpha/d2019-05-15_simulations/gammaonly_wobble_cut.pdf")
    title = "Wobble MC (1deg)"
    process(path, output, title, CUTS_WOBBLE)

    path = get_data("d191018_alpha/extract_alpha_mc/d2019-10-03_simulations_gamma3deg_onoff.h5")
    output = get_plot("d191018_alpha/d2019-10-03_simulations/gamma3deg_onoff_nocut.pdf")
    title = "ON/OFF MC (3deg) (No cuts)"
    process(path, output, title, None)
    output = get_plot("d191018_alpha/d2019-10-03_simulations/gamma3deg_onoff_softcut.pdf")
    title = "ON/OFF MC (3deg) (Soft cuts)"
    process(path, output, title, CUTS_ONOFF_SOFT)
    output = get_plot("d191018_alpha/d2019-10-03_simulations/gamma3deg_onoff_harshcut.pdf")
    title = "ON/OFF MC (3deg) (Harsh cuts)"
    process(path, output, title, CUTS_ONOFF_HARSH)

    path = get_data("d191018_alpha/extract_alpha_mc/d2019-10-03_simulations_gamma3deg_wobble.h5")
    output = get_plot("d191018_alpha/d2019-10-03_simulations/gamma3deg_wobble_nocut.pdf")
    title = "Wobble MC (3deg) (No cuts)"
    process(path, output, title, None)
    output = get_plot("d191018_alpha/d2019-10-03_simulations/gamma3deg_wobble_cut.pdf")
    title = "Wobble MC (3deg)"
    process(path, output, title, CUTS_WOBBLE)

    path = get_data("d191018_alpha/extract_alpha_mc/d2019-10-03_simulations_gamma3deg_5off_wobble.h5")
    output = get_plot("d191018_alpha/d2019-10-03_simulations/gamma3deg_5off_wobble_nocut.pdf")
    title = "Wobble MC (3deg) (5 OFF) (No cuts)"
    process(path, output, title, None)
    output = get_plot("d191018_alpha/d2019-10-03_simulations/gamma3deg_5off_wobble_cut.pdf")
    title = "Wobble MC (3deg) (5 OFF)"
    process(path, output, title, CUTS_WOBBLE)

    path = get_data("d191018_alpha/extract_alpha_mc/d2019-10-03_simulations_gammaonly_wobble.h5")
    output = get_plot("d191018_alpha/d2019-10-03_simulations/gammaonly_wobble_nocut.pdf")
    title = "Wobble MC (3deg) (No cuts)"
    process(path, output, title, None)
    output = get_plot("d191018_alpha/d2019-10-03_simulations/gammaonly_wobble_cut.pdf")
    title = "Wobble MC (3deg)"
    process(path, output, title, CUTS_WOBBLE)


if __name__ == '__main__':
    main()
