from CHECLabPy.plotting.setup import Plotter
from CHECLabPy.core.io import HDF5Reader
from CHECLabPySB import get_data, get_plot
import numpy as np
import pandas as pd
from numpy.polynomial.polynomial import polyfit
from os.path import join
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
    def plot(self, hist, edges, label, **kwargs):
        between = (edges[1:] + edges[:-1]) * 0.5
        self.ax.hist(
            between, weights=hist, bins=edges, label=label, **kwargs
        )

    def annotate_region(self, region_size):
        self.ax.axvline(region_size, color='orange', lw=0.5)

    def annotate_li_ma(self, sig_per_sqrthour, rate_on, rate_off, cut, alpha):
        n_hours = (5/sig_per_sqrthour)**2
        self.ax.text(
            0.9, 0.2,
            r"$\sigma_{{Li&Ma}}$ = "f"{sig_per_sqrthour:.2f} "
            r"$\sigma/\sqrt{h}$""\n"
            r"($5\sigma$"f" @ {n_hours:.2f} hours)\n"
            r"$R_{on}$ = "f"{rate_on:.2f} events/s\n"
            r"$R_{off}$ = "f"{rate_off:.2f} events/s\n"
            r"Cut = "f"{cut:.2f} deg\n"
            r"$\alpha$ = "f"{alpha:.2f}",
            transform=self.ax.transAxes,
            horizontalalignment='right',
            verticalalignment='bottom'
        )

    def finish(self):
        self.ax.set_xlabel("Alpha (deg)")
        self.ax.set_ylabel("Events/sec")


class SigVsTime(Plotter):
    def plot(self, time, significance):
        self.ax.plot(time, significance)


def plot_on_off(alpha_on, alpha_off, weights_on, weights_off,
                alpha_li_ma, title, output_path):
    time = np.linspace(1, 2*24*60*60, 1000)
    region_size = 10
    bins = np.linspace(0, 90, 91)

    hist_on, edges_on = np.histogram(alpha_on, weights=weights_on, bins=bins)
    mask = alpha_on <= region_size
    alpha_on_ir = alpha_on[mask]
    weights_on_ir = weights_on[mask]
    hist_on_ir, _ = np.histogram(alpha_on_ir, weights=weights_on_ir)
    rate_on = hist_on_ir.sum()
    n_on = rate_on * time

    hist_off, edges_off = np.histogram(alpha_off, weights=weights_off, bins=bins)
    mask = alpha_off <= region_size
    alpha_off_ir = alpha_off[mask]
    weights_off_ir = weights_off[mask]
    hist_off_ir, _ = np.histogram(alpha_off_ir, weights=weights_off_ir)
    rate_off = hist_off_ir.sum()
    n_off = rate_off * time

    significance = li_ma(n_on, n_off, alpha_li_ma)
    _, sig_per_sqrthour = polyfit(np.sqrt(time/3600), significance, [1])

    p_hist = Hist()
    p_hist.plot(alpha_li_ma*hist_off, edges_off, "OFF", color='black', alpha=0.2)
    p_hist.plot(hist_on, edges_on, "ON", histtype='step')
    p_hist.annotate_region(region_size)
    p_hist.annotate_li_ma(
        sig_per_sqrthour, rate_on, rate_off, region_size, alpha_li_ma
    )
    p_hist.ax.set_title(title)
    p_hist.add_legend(1)
    p_hist.save(output_path)

    p_hist = Hist()
    p_hist.plot((hist_on-alpha_li_ma*hist_off), edges_on, None, histtype='step')
    p_hist.annotate_region(region_size)
    p_hist.annotate_li_ma(
        sig_per_sqrthour, rate_on, rate_off, region_size, alpha_li_ma
    )
    p_hist.ax.set_title(title + " Excess")
    p_hist.save(output_path.replace(".pdf", "_excess.pdf"))


def process(path, output_dir):
    with HDF5Reader(path) as reader:
        df = reader.read("data")
        metadata = reader.get_metadata()
        n_onoff = metadata['n_onoff']

    df = df.loc[
        (df['baseline_mean'] < 11.88) &
        (df['charge_median'] < 11) &
        (df['size_tm_20'] < 24.5) &
        (df['size_tm_40'] < 14.5)
    ]

    # TODO:
    # df = df.loc[df['diffuse'] == 0]
    # alpha0 = df['alpha0'].values
    # alpha1 = df['alpha1'].values
    # df['alpha0'] = alpha1
    # df['alpha1'] = alpha0

    df_on = df#.loc[df['diffuse'] == 0]
    alpha_on = df_on['alpha0'].values
    weights_on = df_on['weights'].values
    df_off = df#.loc[df['diffuse'] == 1]
    alpha_off = np.concatenate([df_off[f'alpha{i}'] for i in range(1, n_onoff)])
    weights_off = np.concatenate([df_off[f'weights'] for i in range(1, n_onoff)])
    plot_on_off(
        alpha_on, alpha_off, weights_on, weights_off, 1/(n_onoff-1),
        "On/Off MC", join(output_dir, "hist_onoff.pdf")
    )

    df_gamma = df.loc[df['diffuse'] == 0]
    df_proton = df.loc[df['diffuse'] == 1]
    half = df_proton.index.size // 2
    df_on = df_proton.iloc[half:]#pd.concat([df_gamma, df_proton.iloc[half:]])
    df_off = df_proton.iloc[:half]
    alpha_on = df_on['alpha0'].values
    weights_on = df_on['weights'].values
    alpha_off = df_off['alpha0'].values
    weights_off = df_off['weights'].values

    # weights_on[:] = 1
    # weights_off[:] = 1

    plot_on_off(
        alpha_on, alpha_off, weights_on, weights_off, 1,
        "Gamma/Proton MC", join(output_dir, "hist_gammavsproton.pdf")
    )

    # hist_on, edges_on = np.histogram(alpha_on, weights=weights, bins=bins)
    # hist_on_uw, _ = np.histogram(alpha_on, bins=bins)
    #
    # hist_off1, edges_off1 = np.histogram(alpha_off1, weights=weights, bins=bins)
    # hist_off1_uw, _ = np.histogram(alpha_off1, bins=bins)
    #
    # mask = alpha_on <= region_size
    # alpha_on_ir = alpha_on[mask]
    # weights_on_ir = weights[mask]
    # hist_on_ir, _ = np.histogram(alpha_on_ir, weights=weights_on_ir)
    # rate_on = hist_on_ir.sum()
    # n_on = rate_on * time
    #
    # mask = alpha_off <= region_size
    # alpha_off_ir = alpha_off[mask]
    # weights_off_ir = weights_off[mask]
    # hist_off_ir, _ = np.histogram(alpha_off_ir, weights=weights_off_ir)
    # rate_off = hist_off_ir.sum()
    # n_off = rate_off * time
    #
    # significance = li_ma(n_on, n_off, alpha_li_ma)
    # _, sig_per_sqrthour = polyfit(np.sqrt(time/3600), significance, [1])
    #
    # p_hist = Hist()
    # p_hist.plot(hist_off1, edges_off1, "OFF", color='black', alpha=0.2)
    # p_hist.plot(hist_on, edges_on, "ON", histtype='step')
    # p_hist.annotate_region(region_size)
    # p_hist.annotate_li_ma(sig_per_sqrthour, rate_on, rate_off, region_size, alpha_li_ma)
    # p_hist.ax.set_title("On/Off MC")
    # p_hist.save(join(output_dir, "hist_onoff.pdf"))
    #
    # p_sig = SigVsTime()
    # p_sig.plot(time, significance)
    # p_sig.save(join(output_dir, "sig_vs_time_onoff.pdf"))
    #
    # # Gamma vs Diffuse Proton
    #
    # diffuse = df['diffuse'].values.astype(np.bool)
    # alpha_gamma = alpha_on[~diffuse]
    # weights_gamma = weights[~diffuse]
    # hist_gamma, edges_gamma = np.histogram(
    #     alpha_gamma, weights=weights_gamma, bins=bins
    # )
    #
    # alpha_proton = alpha_on[diffuse]
    # weights_proton = weights[diffuse]
    # hist_proton, edges_proton = np.histogram(
    #     alpha_proton, weights=weights_proton, bins=bins
    # )
    #
    # mask = alpha_gamma <= region_size
    # alpha_gamma_ir = alpha_gamma[mask]
    # weights_gamma_ir = weights_gamma[mask]
    # hist_gamma_ir, _ = np.histogram(alpha_gamma_ir, weights=weights_gamma_ir)
    # rate_gamma = hist_gamma_ir.sum()
    # n_gamma = rate_gamma * time
    #
    # mask = alpha_proton <= region_size
    # alpha_proton_ir = alpha_proton[mask]
    # weights_proton_ir = weights_proton[mask]
    # hist_proton_ir, _ = np.histogram(alpha_proton_ir, weights=weights_proton_ir)
    # rate_proton = hist_proton_ir.sum()
    # n_proton = rate_proton * time
    #
    # significance = li_ma(n_gamma+n_proton, n_proton, 1)
    # _, sig_per_sqrthour = polyfit(np.sqrt(time/3600), significance, [1])
    #
    # p_hist = Hist()
    # p_hist.plot(hist_proton, edges_proton, "Proton", color='black', alpha=0.2)
    # p_hist.plot(hist_gamma, edges_gamma, "Gamma", histtype='step')
    # p_hist.ax.set_yscale('log')
    # p_hist.annotate_region(region_size)
    # p_hist.annotate_li_ma(
    #     sig_per_sqrthour, rate_gamma+rate_proton, rate_proton, region_size, 1
    # )
    # p_hist.ax.set_title("Gamma/Proton MC")
    # p_hist.save(join(output_dir, "hist_gammavsproton.pdf"))


def main():
    path = get_data("d190918_alpha/alpha_mc.h5")
    output_dir = get_plot("d190918_alpha/alpha_mc")
    process(path, output_dir)


if __name__ == '__main__':
    main()
