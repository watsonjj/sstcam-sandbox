from CHECLabPySB.plotting.setup import Plotter
from CHECLabPySB.old.io import HDF5Reader
import numpy as np
from scipy.stats import binned_statistic as bs
from matplotlib.ticker import FuncFormatter
import os
from IPython import embed


def sum_errors(array):
    return np.sqrt(np.sum(np.power(array, 2)) / array.size)


def bin_points(x, y, yerr):
    bins = np.geomspace(0.1, x.max(), 100)
    x_b = bs(x, x, 'mean', bins=bins)[0]
    y_b = bs(x, y, 'mean', bins=bins)[0]
    yerr_b = bs(x, yerr, sum_errors, bins=bins)[0]
    valid = ~np.isnan(x_b)
    x_b = x_b[valid]
    y_b = y_b[valid]
    yerr_b = yerr_b[valid]
    return x_b, y_b, yerr_b


class IntensityResolutionPlotter(Plotter):
    def __init__(self, n_bins=40, **kwargs):
        super().__init__(**kwargs)
        self.df_pixel = None
        self.df_camera = None
        self.scale_x = None
        self.scale_y = None
        self.n_bins = n_bins
        self.current_color = None

        self.ax.set_xlabel("Average Expected Illumination (photons)")
        self.ax.set_ylabel(r"Fractional Intensity Resolution $\frac{{\sigma_I}}{{I}}$")

    def set_file(self, file):
        path = file.intensity_resolution_path
        dead = file.dead
        with HDF5Reader(path) as reader:
            df_p = reader.read('charge_resolution_pixel')
            self.df_pixel = df_p.loc[~df_p['pixel'].isin(dead)]
            self.df_camera = reader.read('charge_resolution_camera')

        try:
            path = file.fit_intensity_res_path
            if os.path.exists(path):
                with HDF5Reader(path) as reader:
                    df = reader.read('data')
                    self.scale_x = df['x'].values
                    self.scale_y = df['yopct'].values
            else:
                self.scale_x = None
                self.scale_y = None
        except AttributeError:
            self.scale_x = None
            self.scale_y = None

    def _plot(self, x, y, xerr, yerr, label=''):
        self.current_color = self.ax._get_lines.get_next_color()
        (_, caps, _) = self.ax.errorbar(
            x, y, xerr=xerr, yerr=yerr, mew=1, capsize=1, elinewidth=0.5,
            markersize=2, color=self.current_color, label=label, linewidth=0.5, fmt='.',
        )
        for cap in caps:
            cap.set_markeredgewidth(0.5)

    @staticmethod
    def bin_dataframe(df, n_bins=40):
        true = df['true'].values
        min_ = true.min()
        max_ = (true.max() // 500 + 1) * 500
        bins = np.geomspace(0.1, max_, n_bins)
        bins = np.append(bins, 10**(np.log10(bins[-1]) + np.diff(np.log10(bins))[0]))
        df['bin'] = np.digitize(true, bins, right=True) - 1

        log = np.log10(bins)
        between = 10**((log[1:] + log[:-1]) / 2)
        edges = np.repeat(bins, 2)[1:-1].reshape((bins.size-1 , 2))
        edge_l = edges[:, 0]
        edge_r = edges[:, 1]
        df['between'] = between[df['bin']]
        df['edge_l'] = edge_l[df['bin']]
        df['edge_r'] = edge_r[df['bin']]

        return df

    def plot_average(self, label='', n_bins=40):
        df_binned = self.bin_dataframe(self.df_pixel, n_bins)
        df_camera_mean = df_binned.groupby(['bin']).mean()
        bin_ = df_camera_mean.index
        x = df_camera_mean['true'].values
        y = df_camera_mean['charge_resolution'].values
        yerr = None
        xerr = None
        df_camera_std = df_binned.groupby(['bin']).std()
        yerr = df_camera_std['charge_resolution'].loc[bin_].values
        if 'true_err' in df_binned.columns:
            df_err = df_binned[['bin', 'true_err']].groupby(['bin']).apply(sum_errors)
            xerr = df_err['true_err'].loc[bin_].values
        self._plot(x, y, xerr, yerr, label)

    def plot_pixel(self, pixel, label=''):
        df_binned = self.bin_dataframe(self.df_pixel)
        df_p = df_binned.loc[df_binned['pixel'] == pixel]
        df_mean = df_p.groupby('bin').mean()
        bin_ = df_mean.index
        x = df_mean['true'].values
        y = df_mean['charge_resolution'].values
        yerr = None
        xerr = None
        if 'true_err' in df_binned.columns:
            df_err = df_p[['bin', 'true_err']].groupby(['bin']).apply(sum_errors)
            xerr = df_err['true_err'].loc[bin_].values
        self._plot(x, y, xerr, yerr, label)

    def plot_camera(self, label=''):
        df_binned = self.bin_dataframe(self.df_camera)
        df_camera_mean = df_binned.groupby(['bin']).agg({'charge_resolution': 'mean', 'true': 'mean', 'n': 'sum'})
        x = df_camera_mean['true']
        y = df_camera_mean['charge_resolution']
        yerr = 1/np.sqrt(df_camera_mean['n'].values)
        self._plot(x, y, None, yerr, label)

    def plot_scaling(self, label=''):
        if self.scale_x is not None:
            label = label + " (Improved SiPM Scaling)"
            self.ax.plot(self.scale_x, self.scale_y, ':', color=self.current_color, alpha=0.5, label=label)

    def finish(self):
        self.ax.set_xscale('log')
        self.ax.get_xaxis().set_major_formatter(
            FuncFormatter(lambda x, _: '{:g}'.format(x)))
        self.ax.set_yscale('log')
        self.ax.get_yaxis().set_major_formatter(
            FuncFormatter(lambda y, _: '{:g}'.format(y)))

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
        sigma_0 = np.sqrt(nsb * t_w + n_e**2)
        sigma_enf = 1 + enf
        sigma_q = np.sqrt(sigma_0**2 + sigma_enf**2 * q + sigma_g**2 * q**2)
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
        self.ax.plot(true, requirement, '--', color='black', label="Requirement")

    def plot_requirement_highNSB(self, true):
        requirement = self.requirement_highNSB(true)
        self.ax.plot(true, requirement, ':', color='black', label="Requirement (HighNSB)")

    def plot_poisson(self, true):
        poisson = self.poisson(true)
        self.ax.plot(true, poisson, '--', color='grey', label="Poisson")


class IntensityResolutionWRRPlotter(IntensityResolutionPlotter):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ax.set_xlabel("Average Expected Illumination (photons)")
        self.ax.set_ylabel(r"$\frac{{\sigma_I}}{{I}}$ / Requirement")

    def _plot(self, x, y, xerr, yerr, label=''):
        y = y / self.requirement(x)
        if yerr is not None:
            yerr = yerr / self.requirement(x)
        super()._plot(x, y, xerr, yerr, label)

    def plot_scaling(self, label=''):
        if self.scale_x is not None:
            label = label + " (Prod4 Scaling)"
            y = self.scale_y / self.requirement(self.scale_x)
            self.ax.plot(self.scale_x, y, color=self.current_color, label=label)

    def plot_requirement(self, true):
        requirement = self.requirement(true)
        requirement /= self.requirement(true)
        self.ax.plot(true, requirement, '--', color='black', label="Requirement")

    def plot_requirement_highNSB(self, true):
        requirement = self.requirement_highNSB(true)
        requirement /= self.requirement(true)
        self.ax.plot(true, requirement, '--', color='black', label="Requirement (HighNSB)")

    def plot_poisson(self, true):
        poisson = self.poisson(true)
        poisson /= self.requirement(true)
        self.ax.plot(true, poisson, '--', color='grey', label="Poisson")

    def finish(self):
        self.ax.set_xscale('log')
        self.ax.get_xaxis().set_major_formatter(
            FuncFormatter(lambda x, _: '{:g}'.format(x)))
