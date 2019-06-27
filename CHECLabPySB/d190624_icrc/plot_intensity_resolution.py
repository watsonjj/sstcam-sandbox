from CHECLabPy.plotting.setup import Plotter
from CHECLabPySB import get_data, get_plot
import numpy as np
import pandas as pd
from matplotlib.ticker import FuncFormatter
import matplotlib as mpl

mpl.rcParams.update({"legend.fontsize": 1})


def sum_errors(array):
    return np.sqrt(np.sum(np.power(array, 2)) / array.size)


# def bin_points(x, y, yerr):
#     bins = np.geomspace(0.1, x.max(), 100)
#     x_b = bs(x, x, 'mean', bins=bins)[0]
#     y_b = bs(x, y, 'mean', bins=bins)[0]
#     yerr_b = bs(x, yerr, sum_errors, bins=bins)[0]
#     valid = ~np.isnan(x_b)
#     x_b = x_b[valid]
#     y_b = y_b[valid]
#     yerr_b = yerr_b[valid]
#     return x_b, y_b, yerr_b


def bin_dataframe(df, n_bins=40):
    true = df['true'].values
    min_ = true.min()
    max_ = (true.max() // 500 + 1) * 500
    bins = np.geomspace(0.1, max_, n_bins)
    bins = np.append(bins,
                     10 ** (np.log10(bins[-1]) + np.diff(np.log10(bins))[0]))
    df['bin'] = np.digitize(true, bins, right=True) - 1

    log = np.log10(bins)
    between = 10 ** ((log[1:] + log[:-1]) / 2)
    edges = np.repeat(bins, 2)[1:-1].reshape((bins.size - 1, 2))
    edge_l = edges[:, 0]
    edge_r = edges[:, 1]
    df['between'] = between[df['bin']]
    df['edge_l'] = edge_l[df['bin']]
    df['edge_r'] = edge_r[df['bin']]
    return df


class IRPlotter(Plotter):
    def get_color(self):
        return self.ax._get_lines.get_next_color()

    def plot(self, x, y, xerr, yerr, **kwargs):
        l = self.ax.errorbar(
            x, y, xerr=xerr, yerr=yerr, mew=1, capsize=0.7, elinewidth=0.25,
            markersize=1, linewidth=0.25, fmt='.', **kwargs
        )
        for cap in l[1]:
            cap.set_markeredgewidth(0.5)
        return l

    @staticmethod
    def limit_curves(n, nsb, t_w, n_e, sigma_g, enf, pde):
        """
        Equation for calculating the Goal and Requirement curves, as defined
        in SCI-MC/121113.
        https://portal.cta-observatory.org/recordscentre/Records/SCI/
        SCI-MC/measurment_errors_system_performance_1YQCBC.pdf

        Parameters
        ----------
        n : ndarray
            Number of photons (variable).
        nsb : float
            Number of NSB photons.
        t_w : float
            Effective signal readout window size.
        n_e : float
            Electronic noise
        sigma_g : float
            Multiplicative errors of the gain.
        enf : float
            Excess noise factor.
        """
        q = n * pde
        sigma_0 = np.sqrt(nsb * t_w + n_e ** 2)
        sigma_enf = 1 + enf
        sigma_q = np.sqrt(
            sigma_0 ** 2 + sigma_enf ** 2 * q + sigma_g ** 2 * q ** 2)
        return sigma_q / q

    @staticmethod
    def requirement(n):
        """
        CTA requirement curve.

        Parameters
        ----------
        n : ndarray
            Number of photons
        """
        nsb = 0.125
        t_w = 15
        n_e = 0.87
        sigma_g = 0.1
        enf = 0.2
        pde = 0.25
        lc = __class__.limit_curves
        requirement = lc(n, nsb, t_w, n_e, sigma_g, enf, pde)

        max_photons = 4000
        min_photons = 4
        requirement[(n > max_photons) & (n < min_photons)] = np.nan

        return requirement

    @staticmethod
    def requirement_highNSB(n):
        nsb = 1.25
        t_w = 15
        n_e = 0.87
        sigma_g = 0.1
        enf = 0.2
        pde = 0.25
        lc = __class__.limit_curves
        requirement = lc(n, nsb, t_w, n_e, sigma_g, enf, pde)

        max_photons = 4000
        min_photons = 4
        requirement[(n > max_photons) & (n < min_photons)] = np.nan

        return requirement

    @staticmethod
    def poisson(n):
        """
        Poisson limit curve.

        Parameters
        ----------
        n : ndarray
            Number of photons
        """
        poisson = np.sqrt(n) / n
        return poisson

    def plot_requirement(self, true):
        requirement = self.requirement(true)
        l, = self.ax.plot(true, requirement, '--', color='black',
                     label="Requirement")
        return l

    def plot_requirement_highNSB(self, true):
        requirement = self.requirement_highNSB(true)
        l, = self.ax.plot(true, requirement, ':', color='black',
                     label="Requirement (HighNSB)")
        return l

    def plot_poisson(self, true):
        poisson = self.poisson(true)
        l, = self.ax.plot(true, poisson, '--', color='grey', label="Poisson")
        return l

    def finish(self):
        self.ax.set_xscale('log')
        self.ax.get_xaxis().set_major_formatter(
            FuncFormatter(lambda x, _: '{:g}'.format(x)))
        self.ax.set_yscale('log')
        self.ax.get_yaxis().set_major_formatter(
            FuncFormatter(lambda y, _: '{:g}'.format(y)))
        self.ax.set_xlim([3, 1000])
        self.ax.set_ylim([0.01, 20])
        self.ax.set_xlabel("Average Expected Illumination (photons)")
        self.ax.set_ylabel(r"Fractional Intensity Resolution $\frac{{\sigma_I}}{{I}}$")


def main():

    p_ir = IRPlotter()

    low_color = p_ir.get_color()
    mc_color = p_ir.get_color()
    high_color = p_ir.get_color()

    # Low NSB data points
    path = get_data("d181031_sst_rfi/intensity_resolution/intensity_resolution/d181010_LabSM_40MHz_100mV.h5")
    with pd.HDFStore(path) as store:
        df_pixel = store['charge_resolution_pixel']
    df_binned = bin_dataframe(df_pixel, 40)
    df_camera_mean = df_binned.groupby(['bin']).mean()
    df_camera_mean = df_camera_mean.loc[df_camera_mean['true'] < 1000]
    bin_ = df_camera_mean.index
    x = df_camera_mean['true'].values
    y = df_camera_mean['charge_resolution'].values
    df_camera_std = df_binned.groupby(['bin']).std()
    yerr = df_camera_std['charge_resolution'].loc[bin_].values
    df_err = df_binned[['bin', 'true_err']].groupby(['bin']).apply(sum_errors)
    xerr = df_err['true_err'].loc[bin_].values
    l_low = p_ir.plot(x, y, xerr, yerr, label="Lab (Nominal NSB)", color=low_color)

    path = get_data("d181031_sst_rfi/intensity_resolution/fit_intensity_res/d181010_LabSM_40MHz_100mV.h5")
    with pd.HDFStore(path) as store:
        df = store['data']
    x = df['x'].values
    y = df['yopct'].values
    l_low_prog, = p_ir.ax.plot(
        x, y, ':', color=low_color, alpha=1,
        label="Lab (Nominal NSB) (Projected Improvement)"
    )

    # MCLab data points
    path = get_data("d181031_sst_rfi/intensity_resolution/intensity_resolution/d180907_MCLab_opct40_40MHz.h5")
    with pd.HDFStore(path) as store:
        df_pixel = store['charge_resolution_pixel']
    df_binned = bin_dataframe(df_pixel, 40)
    df_camera_mean = df_binned.groupby(['bin']).mean()
    df_camera_mean = df_camera_mean.loc[df_camera_mean['true'] < 1000]
    bin_ = df_camera_mean.index
    x = df_camera_mean['true'].values
    y = df_camera_mean['charge_resolution'].values
    df_camera_std = df_binned.groupby(['bin']).std()
    yerr = df_camera_std['charge_resolution'].loc[bin_].values
    df_err = df_binned[['bin', 'true_err']].groupby(['bin']).apply(sum_errors)
    xerr = df_err['true_err'].loc[bin_].values
    l_mc = p_ir.plot(x, y, xerr, yerr, label="Lab MC Sim. (Nominal NSB)", color=mc_color, marker='^')

    # High NSB data points
    path = get_data(
        "d181031_sst_rfi/intensity_resolution/intensity_resolution/d181010_LabSM_1000MHz_100mV.h5")
    with pd.HDFStore(path) as store:
        df_pixel = store['charge_resolution_pixel']
    df_binned = bin_dataframe(df_pixel, 40)
    df_camera_mean = df_binned.groupby(['bin']).mean()
    df_camera_mean = df_camera_mean.loc[df_camera_mean['true'] < 1000]
    bin_ = df_camera_mean.index
    x = df_camera_mean['true'].values
    y = df_camera_mean['charge_resolution'].values
    df_camera_std = df_binned.groupby(['bin']).std()
    yerr = df_camera_std['charge_resolution'].loc[bin_].values
    df_err = df_binned[['bin', 'true_err']].groupby(['bin']).apply(sum_errors)
    xerr = df_err['true_err'].loc[bin_].values
    l_high = p_ir.plot(x, y, xerr, yerr, label="Lab (Nominal NSB)", color=high_color, marker="<")

    path = get_data(
        "d181031_sst_rfi/intensity_resolution/fit_intensity_res/d181010_LabSM_1000MHz_100mV.h5")
    with pd.HDFStore(path) as store:
        df = store['data']
    x = df['x'].values
    y = df['yopct'].values
    l_high_proj, = p_ir.ax.plot(
        x, y, ':', color=high_color, alpha=1,
        label="Lab (Nominal NSB) (Projected Improvement)"
    )

    true = np.geomspace(x.min(), 1100, 100)
    l_poisson = p_ir.plot_poisson(true)
    # l_req = p_ir.plot_requirement(true)
    # l_req_high = p_ir.plot_requirement_highNSB(true)

    p_ir.ax.legend([
        l_poisson,
        # l_req,
        # l_req_high,
        l_low,
        l_low_prog,
        l_mc,
        l_high,
        l_high_proj,
    ], [
        "Poisson Limit",
        # "Requirement",
        # "Requirement (High NSB)",
        "Lab (Nominal NSB)",
        "Lab (Nominal NSB) (Proj. Improvement)",
        "Lab MC Sim. (Nominal NSB)",
        "Lab (High NSB)",
        "Lab (High NSB) (Proj. Improvement)",
    ], loc="best", frameon=False)

    p_ir.save(get_plot("d190624_icrc/res.pdf"))


if __name__ == '__main__':
    main()