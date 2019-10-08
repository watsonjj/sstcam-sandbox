from CHECLabPy.plotting.setup import Plotter
from CHECLabPy.core.io import HDF5Reader
from CHECLabPySB import get_data, get_plot
from CHECLabPySB.d190918_alpha import *
import numpy as np
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


class Hist(Plotter):
    def plot(self, counts, counts_err, edges, label):
        between = (edges[1:] + edges[:-1]) * 0.5
        caps = self.ax.errorbar(
            between, counts, yerr=counts_err, xerr=np.diff(edges) * 0.5,
            linestyle='', capsize=1, elinewidth=0.5, label=label
        )
        for cap in caps[1]:
            cap.set_markeredgewidth(0.5)

    def annotate_region(self, region_size):
        self.ax.axvline(region_size, color='orange', lw=0.5)

    def finish(self):
        self.ax.set_xlabel("Alpha (deg)")
        self.ax.set_ylabel("Events")


class SigVsTime(Plotter):
    def plot(self, time, significance):
        self.ax.plot(np.sqrt(time), significance)


def process(path, output, title, cuts):
    with HDF5Reader(path) as reader:
        df_on = reader.read("on")
        df_off = reader.read("off")
        metadata = reader.get_metadata()
        alpha_li_ma = metadata['alpha_li_ma']
        # obstime = metadata['obstime'].total_seconds() / 3600

    if cuts is not None:
        df_on = df_on.query(cuts)
        df_off = df_off.query(cuts)

    # obstime = df_on.

    bins = np.linspace(0, 90, 91)

    alpha_on = df_on['alpha'].values
    n_on_bins, edges_on = np.histogram(alpha_on, bins=bins)
    n_on_err_bins = np.sqrt(n_on_bins)
    n_on = (alpha_on <= REGION_SIZE).sum()

    alpha_off = df_off['alpha'].values
    n_off_bins, edges_off = np.histogram(alpha_off, bins=bins)
    n_off_err_bins = np.sqrt(n_off_bins)
    n_off = (alpha_off <= REGION_SIZE).sum()

    significance = li_ma(n_on, n_off, alpha_li_ma)

    n_off_bins = n_off_bins * alpha_li_ma
    n_off_err_bins = n_off_err_bins * alpha_li_ma

    p_hist = Hist()
    p_hist.plot(n_off_bins, n_off_err_bins, edges_off, "OFF")
    p_hist.plot(n_on_bins, n_on_err_bins, edges_on, "ON")
    p_hist.annotate_region(REGION_SIZE)
    p_hist.ax.text(
        0.95, 0.05,
        # r"$T_{{obs}}$ = "f"{obstime:.2f} hours \n"
        r"$\sigma_{{Li&Ma}}$ = "f"{significance:.2f}\n"
        r"$N_{on}$ = "f"{n_on} events\n"
        r"$N_{off}$ = "f"{n_off} events ({n_off*alpha_li_ma:.2f})\n"
        r"Cut = "f"{REGION_SIZE:.2f} deg\n"
        r"$\alpha$ = "f"{alpha_li_ma:.2f}",
        transform=p_hist.ax.transAxes,
        horizontalalignment='right',
        verticalalignment='bottom',
        bbox=dict(
            boxstyle="round", fc='blue', alpha=0.7
        )
    )
    p_hist.ax.set_title(title)
    p_hist.add_legend(1)
    p_hist.save(output)


def main():
    cuts_base = CUTS_WOBBLE
    cuts_base = cuts_base + (
        "&(seperation < 2)"
    )

    path = get_data("d190918_alpha/onsky_wobble.h5")
    output = get_plot("d190918_alpha/onsky/ALL.pdf")
    title = "ALL"
    process(path, output, title, cuts_base)

    path = get_data("d190918_alpha/onsky_wobble_1off.h5")
    output = get_plot("d190918_alpha/onsky/ALL_1off.pdf")
    title = "ALL (1 OFF)"
    process(path, output, title, cuts_base)

    path = get_data("d190918_alpha/onsky_wobble.h5")
    cuts = cuts_base + (
        "&(t_cpu < '2019-06-01')"
    )
    output = get_plot("d190918_alpha/onsky/FIRST.pdf")
    title = "FIRST"
    process(path, output, title, cuts)

    path = get_data("d190918_alpha/onsky_wobble_1off.h5")
    cuts = cuts_base + (
        "&(t_cpu < '2019-06-01')"
    )
    output = get_plot("d190918_alpha/onsky/FIRST_1off.pdf")
    title = "FIRST (1 OFF)"
    process(path, output, title, cuts)

    path = get_data("d190918_alpha/onsky_wobble.h5")
    cuts = cuts_base + (
        "&(t_cpu > '2019-06-01')"
    )
    output = get_plot("d190918_alpha/onsky/SECOND.pdf")
    title = "SECOND"
    process(path, output, title, cuts)

    path = get_data("d190918_alpha/onsky_wobble_1off.h5")
    cuts = cuts_base + (
        "&(t_cpu > '2019-06-01')"
    )
    output = get_plot("d190918_alpha/onsky/SECOND_1off.pdf")
    title = "SECOND (1 OFF)"
    process(path, output, title, cuts)

    path = get_data("d190918_alpha/onsky_wobble.h5")
    cuts = cuts_base + (
        "&(source_name == 'mrk501')"
    )
    output = get_plot("d190918_alpha/onsky/MRK501.pdf")
    title = "MRK501"
    process(path, output, title, cuts)

    path = get_data("d190918_alpha/onsky_wobble_1off.h5")
    cuts = cuts_base + (
        "&(source_name == 'mrk501')"
    )
    output = get_plot("d190918_alpha/onsky/MRK501_1off.pdf")
    title = "MRK501 (1 OFF)"
    process(path, output, title, cuts)

    path = get_data("d190918_alpha/onsky_wobble.h5")
    cuts = cuts_base + (
        "&(source_name == 'mrk501')"
        "&(t_cpu < '2019-06-01')"
    )
    output = get_plot("d190918_alpha/onsky/MRK501_FIRST.pdf")
    title = "MRK501_FIRST"
    process(path, output, title, cuts)

    path = get_data("d190918_alpha/onsky_wobble_1off.h5")
    cuts = cuts_base + (
        "&(source_name == 'mrk501')"
        "&(t_cpu < '2019-06-01')"
    )
    output = get_plot("d190918_alpha/onsky/MRK501_FIRST_1off.pdf")
    title = "MRK501_FIRST (1 OFF)"
    process(path, output, title, cuts)

    path = get_data("d190918_alpha/onsky_wobble.h5")
    cuts = cuts_base + (
        "&(source_name == 'mrk501')"
        "&(t_cpu < '2019-05-05')"
    )
    output = get_plot("d190918_alpha/onsky/MRK501_BEST.pdf")
    title = "MRK501_BEST"
    process(path, output, title, cuts)

    path = get_data("d190918_alpha/onsky_wobble_1off.h5")
    cuts = cuts_base + (
        "&(source_name == 'mrk501')"
        "&(t_cpu < '2019-05-05')"
    )
    output = get_plot("d190918_alpha/onsky/MRK501_BEST_1off.pdf")
    title = "MRK501_BEST (1 OFF)"
    process(path, output, title, cuts)

    path = get_data("d190918_alpha/onsky_wobble.h5")
    cuts = cuts_base + (
        "&(source_name == 'mrk421')"
    )
    output = get_plot("d190918_alpha/onsky/MRK421.pdf")
    title = "MRK421"
    process(path, output, title, cuts)

    path = get_data("d190918_alpha/onsky_wobble_1off.h5")
    cuts = cuts_base + (
        "&(source_name == 'mrk421')"
    )
    output = get_plot("d190918_alpha/onsky/MRK421_1off.pdf")
    title = "MRK421 (1 OFF)"
    process(path, output, title, cuts)

    path = get_data("d190918_alpha/onsky_wobble.h5")
    cuts = cuts_base + (
        "&(source_name == 'mrk421')"
        "&(t_cpu < '2019-06-01')"
    )
    output = get_plot("d190918_alpha/onsky/MRK421_FIRST.pdf")
    title = "MRK421_FIRST"
    process(path, output, title, cuts)

    path = get_data("d190918_alpha/onsky_wobble_1off.h5")
    cuts = cuts_base + (
        "&(source_name == 'mrk421')"
        "&(t_cpu < '2019-06-01')"
    )
    output = get_plot("d190918_alpha/onsky/MRK421_FIRST_1off.pdf")
    title = "MRK421_FIRST (1 OFF)"
    process(path, output, title, cuts)

    path = get_data("d190918_alpha/onsky_wobble.h5")
    cuts = cuts_base + (
        "&(source_name == 'mrk421')"
        "&(t_cpu < '2019-05-05')"
    )
    output = get_plot("d190918_alpha/onsky/MRK421_BEST.pdf")
    title = "MRK421_BEST"
    process(path, output, title, cuts)

    path = get_data("d190918_alpha/onsky_wobble_1off.h5")
    cuts = cuts_base + (
        "&(source_name == 'mrk421')"
        "&(t_cpu < '2019-05-05')"
    )
    output = get_plot("d190918_alpha/onsky/MRK421_BEST_1off.pdf")
    title = "MRK421_BEST (1 OFF)"
    process(path, output, title, cuts)

    path = get_data("d190918_alpha/onsky_wobble.h5")
    cuts = cuts_base + (
        "&(source_name == 'PG1553+113')"
        "&(t_cpu < '2019-05-05')"
    )
    output = get_plot("d190918_alpha/onsky/PG1553+113.pdf")
    title = "PG1553+113"
    process(path, output, title, cuts)

    path = get_data("d190918_alpha/onsky_wobble_1off.h5")
    cuts = cuts_base + (
        "&(source_name == 'PG1553+113')"
        "&(t_cpu < '2019-05-05')"
    )
    output = get_plot("d190918_alpha/onsky/PG1553+113_1off.pdf")
    title = "PG1553+113 (1 OFF)"
    process(path, output, title, cuts)


if __name__ == '__main__':
    main()
