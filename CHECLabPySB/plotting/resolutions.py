from ThesisAnalysis.plotting.setup import ThesisPlotter
from ThesisAnalysis import ThesisHDF5Reader
import numpy as np
from scipy.stats import binned_statistic as bs
from matplotlib.ticker import FuncFormatter
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


class ChargeResolutionPlotter(ThesisPlotter):
    def __init__(self, n_bins=40, **kwargs):
        super().__init__(**kwargs)
        self.df_pixel = None
        self.df_camera = None
        self.n_bins = n_bins

        self.ax.set_xlabel("Average Expected Charge (p.e.)")
        self.ax.set_ylabel(r"Fractional Charge Resolution $\frac{{\sigma_Q}}{{Q}}$")

    def set_file(self, file):
        path = file.charge_resolution_path
        dead = file.dead
        with ThesisHDF5Reader(path) as reader:
            df_p = reader.read('charge_resolution_pixel')
            self.df_pixel = df_p.loc[~df_p['pixel'].isin(dead)]
            self.df_camera = reader.read('charge_resolution_camera')

    def _plot(self, x, y, xerr, yerr, label=''):
        color = self.ax._get_lines.get_next_color()
        (_, caps, _) = self.ax.errorbar(
            x, y, xerr=xerr, yerr=yerr, mew=1, capsize=1, elinewidth=0.5,
            markersize=2, color=color, label=label, linewidth=0.5, fmt='.',
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
        x = self.df_camera['true']
        y = self.df_camera['charge_resolution']
        self._plot(x, y, None, label)

    def finish(self):
        self.ax.set_xscale('log')
        self.ax.get_xaxis().set_major_formatter(
            FuncFormatter(lambda x, _: '{:g}'.format(x)))
        self.ax.set_yscale('log')
        self.ax.get_yaxis().set_major_formatter(
            FuncFormatter(lambda y, _: '{:g}'.format(y)))

    @staticmethod
    def limit_curves(q, nsb, t_w, n_e, sigma_g, enf):
        """
        Equation for calculating the Goal and Requirement curves, as defined
        in SCI-MC/121113.
        https://portal.cta-observatory.org/recordscentre/Records/SCI/
        SCI-MC/measurment_errors_system_performance_1YQCBC.pdf

        Parameters
        ----------
        q : ndarray
            Number of photoeletrons (variable).
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
        sigma_0 = np.sqrt(nsb * t_w + n_e**2)
        sigma_enf = 1 + enf
        sigma_q = np.sqrt(sigma_0**2 + sigma_enf**2 * q + sigma_g**2 * q**2)
        return sigma_q / q

    @staticmethod
    def requirement(q):
        """
        CTA requirement curve.

        Parameters
        ----------
        q : ndarray
            Number of photoeletrons
        """
        nsb = 0.125
        t_w = 15
        n_e = 0.87
        sigma_g = 0.1
        enf = 0.2
        defined_npe = 1000
        lc = ChargeResolutionPlotter.limit_curves
        requirement = lc(q, nsb, t_w, n_e, sigma_g, enf)
        requirement[q > defined_npe] = np.nan

        return requirement

    @staticmethod
    def poisson(q):
        """
        Poisson limit curve.

        Parameters
        ----------
        q : ndarray
            Number of photoeletrons
        """
        poisson = np.sqrt(q) / q
        return poisson

    def plot_requirement(self, true):
        requirement = self.requirement(true)
        self.ax.plot(true, requirement, '--', color='black', label="Requirement")

    def plot_poisson(self, true):
        poisson = self.poisson(true)
        self.ax.plot(true, poisson, '--', color='grey', label="Poisson")


class ChargeResolutionWRRPlotter(ChargeResolutionPlotter):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ax.set_xlabel("Average Expected Charge (p.e.)")
        self.ax.set_ylabel(r"$\frac{{\sigma_Q}}{{Q}}$ / Requirement")

    def _plot(self, x, y, xerr, yerr, label=''):
        y = y / self.requirement(x)
        if yerr is not None:
            yerr = yerr / self.requirement(x)
        super()._plot(x, y, xerr, yerr, label)

    def plot_requirement(self, true):
        requirement = self.requirement(true)
        requirement /= self.requirement(true)
        self.ax.plot(true, requirement, '--', color='black', label="Requirement")

    def plot_poisson(self, true):
        poisson = self.poisson(true)
        poisson /= self.requirement(true)
        self.ax.plot(true, poisson, '--', color='grey', label="Poisson")

    def finish(self):
        self.ax.set_xscale('log')
        self.ax.get_xaxis().set_major_formatter(
            FuncFormatter(lambda x, _: '{:g}'.format(x)))


class ChargeMeanPlotter(ThesisPlotter):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.df_pixel = None
        self.df_camera = None
        self.x_min = None
        self.x_max = None

    def set_path(self, path):
        with ThesisHDF5Reader(path) as reader:
            self.df_pixel = reader.read('charge_statistics_pixel')
            self.df_camera = reader.read('charge_statistics_camera')

    def _plot(self, x, y, yerr, label=''):
        y /= x
        yerr /= x
        # yerr = None
        color = self.ax._get_lines.get_next_color()

        (_, caps, _) = self.ax.errorbar(
            x, y, yerr=yerr, mew=1, capsize=3, elinewidth=0.7,
            markersize=3, color=color, label=label
        )
        for cap in caps:
            cap.set_markeredgewidth(0.7)

        if self.x_min is None or self.x_min > x.min():
            self.x_min = x.min()
        if self.x_max is None or self.x_max < x.max():
            self.x_max = x.max()

    def plot_pixel(self, pixel, label=''):
        df_pixel = self.df_pixel.loc[self.df_pixel['pixel'] == pixel]
        x = df_pixel['amplitude']
        y = df_pixel['mean']
        yerr = df_pixel['std']
        x, y, yerr = bin_points(x, y, yerr)
        self._plot(x, y, yerr, label)

    def plot_camera(self, label=''):
        x = self.df_camera['amplitude']
        y = self.df_camera['mean']
        yerr = self.df_camera['std']
        x, y, yerr = bin_points(x, y, yerr)
        self._plot(x, y, yerr, label)

    def finish(self):
        p = np.linspace(self.x_min, self.x_max, 1000)
        self.ax.plot(p, p/p, '--', color='grey')

        self.ax.set_xlabel("Average Expected Charge (p.e.)")
        self.ax.set_ylabel("Average Measured Charge / Average Expected Charge")
        self.ax.set_xscale('log')
        self.ax.get_xaxis().set_major_formatter(
            FuncFormatter(lambda x, _: '{:g}'.format(x)))
        # self.ax.set_yscale('log')
        # self.ax.get_yaxis().set_major_formatter(
        #     FuncFormatter(lambda y, _: '{:g}'.format(y)))
