from CHECLabPySB import get_checs, get_data, get_plot
from CHECLabPy.core.io import TIOReader
from CHECLabPy.core.io import HDF5Reader
from CHECLabPy.plotting.setup import Plotter
from TargetCalibSB.tf import TFDC
from TargetCalibSB import VpedCalibrator, correct_overflow
from TargetCalibSB.pedestal import PedestalTargetCalib
from TargetCalibSB import get_cell_ids_for_waveform
import numpy as np
import pandas as pd
from tqdm import tqdm
from glob import glob
from numba import njit, prange
import re
import numpy as np
from matplotlib.ticker import FuncFormatter
from IPython import embed


class ChargeResolutionPlot(Plotter):
    def plot(self, x, y, xerr=None, yerr=None, label=None):
        # self.current_color = self.ax._get_lines.get_next_color()
        (_, caps, _) = self.ax.errorbar(
            x, y, xerr=xerr, yerr=yerr, mew=1, capsize=1, elinewidth=0.5,
            markersize=2, label=label, linewidth=0.5, fmt='.',
        )
        for cap in caps:
            cap.set_markeredgewidth(0.5)

    def finish(self):
        self.ax.set_xlabel("Average Expected Charge (p.e.)")
        self.ax.set_ylabel(r"Fractional Charge Resolution $\frac{{\sigma_Q}}{{Q}}$")

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
        lc = __class__.limit_curves
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


class ChargePlot(Plotter):
    def plot(self, x, y, xerr=None, yerr=None, **kwargs):
        # color = self.ax._get_lines.get_next_color()
        (_, caps, _) = self.ax.errorbar(
            x, y, xerr=xerr, yerr=yerr, mew=1, capsize=1, elinewidth=0.5,
            markersize=2, linewidth=0.5, fmt='.', **kwargs
        )
        for cap in caps:
            cap.set_markeredgewidth(0.5)


def calculate_charge_resolution(path):
    with HDF5Reader(path) as reader:
        df = reader.read("data")

    n_channels = np.unique(df['channel']).size
    n_true = np.unique(df['amplitude']).size
    print(np.unique(df['amplitude']))
    true = np.zeros((n_channels, n_true))
    resolution = np.zeros((n_channels, n_true))
    average = np.zeros((n_channels, n_true))
    std = np.zeros((n_channels, n_true))
    for channel, group in df.groupby('channel'):
        # Calibrate
        cal_amplitude = 20
        assumed_gain = 4  # mV/p.e.
        cal_charge = group.loc[group['amplitude'] == cal_amplitude, 'charge'].values
        cal_average = cal_charge.mean()
        factor = (cal_amplitude / assumed_gain) / cal_average

        group = group.copy()
        group['measured'] = group['charge'].values * factor
        group['true'] = group['amplitude'].values / assumed_gain
        group['n'] = 1
        group['sum'] = np.power(group['measured'] - group['true'], 2)

        summed = group.groupby(['true']).sum()
        true_channel = summed.index.values
        sum_channel = summed['sum'].values
        n_channel = summed['n'].values
        true[channel] = true_channel
        resolution[channel] = np.sqrt(sum_channel / n_channel) / np.abs(true_channel)
        # resolution[channel] = np.sqrt((sum_channel / n_channel) + true_channel) / np.abs(true_channel)

        average_df = group.groupby(['true']).mean()
        average[channel] = average_df['measured'].values
        std_df = group.groupby(['true']).std()
        std[channel] = std_df['measured'].values

    return true, resolution, average, std


def main():
    path_dc_ext_23 = get_data("d191122_dc_tf/charge/dc_externalsync_23deg_charge.h5")
    path_ac_23 = get_data("d191122_dc_tf/charge/ac_23deg_charge.h5")
    path_po_23 = get_data("d191122_dc_tf/charge/pedonly_23deg_charge.h5")

    true_dc_ext_23, res_dc_ext_23, average_dc_ext_23, std_dc_ext_23 = calculate_charge_resolution(path_dc_ext_23)
    true_ac_23, res_ac_23, average_ac_23, std_ac_23 = calculate_charge_resolution(path_ac_23)
    true_po_23, res_po_23, average_po_23, std_po_23 = calculate_charge_resolution(path_po_23)

    channel = 8
    true_dc = true_dc_ext_23.mean(0)
    mean_res_dc = res_dc_ext_23.mean(0)
    std_res_dc = res_dc_ext_23.std(0)
    true_ac = true_ac_23.mean(0)
    mean_res_ac = res_ac_23.mean(0)
    std_res_ac = res_ac_23.std(0)
    true_po = true_po_23.mean(0)
    mean_res_po = res_po_23.mean(0)
    std_res_po = res_po_23.std(0)

    bias_dc = average_dc_ext_23.mean(0) / true_dc
    rms_dc = std_dc_ext_23.mean(0) / true_dc
    bias_ac = average_ac_23.mean(0) / true_ac
    rms_ac = std_ac_23.mean(0) / true_ac
    bias_po = average_po_23.mean(0) / true_po
    rms_po = std_po_23.mean(0) / true_po

    output_path = get_plot(f"d191122_dc_tf/plot_charge_resolution/cr.pdf")
    p_cr = ChargeResolutionPlot()
    p_cr.plot(true_dc, mean_res_dc, yerr=std_res_dc, label="DC")
    p_cr.plot(true_ac, mean_res_ac, yerr=std_res_ac, label="AC")
    p_cr.plot(true_po, mean_res_po, yerr=std_res_po, label="Pedestal Only")
    true = np.geomspace(0.1, 1000, 100)
    p_cr.plot_poisson(true)
    p_cr.plot_requirement(true)
    p_cr.add_legend('best')
    p_cr.save(output_path)

    output_path = get_plot(f"d191122_dc_tf/plot_charge_resolution/bias.pdf")
    p_bias = ChargePlot()
    p_bias.plot(true_dc, bias_dc, yerr=rms_dc, label="DC")
    p_bias.plot(true_ac, bias_ac, yerr=rms_ac, label="AC")
    p_bias.plot(true_po, bias_po, yerr=rms_po, label="Pedestal Only")
    p_bias.add_legend('best')
    p_bias.ax.set_xscale('log')
    p_bias.ax.get_xaxis().set_major_formatter(
        FuncFormatter(lambda x, _: '{:g}'.format(x)))
    p_bias.save(output_path)

    # Bias per channel
    output_path = get_plot(f"d191122_dc_tf/plot_charge_resolution/bias_c.pdf")
    p_bias = ChargePlot()
    for c in range(10):
        bias = average_dc_ext_23[c] / true_dc
        rms = std_dc_ext_23[c] / true_dc
        p_bias.plot(true_dc, bias, label=f"{c}")
    p_bias.add_legend('best')
    p_bias.ax.set_xscale('log')
    p_bias.ax.get_xaxis().set_major_formatter(
        FuncFormatter(lambda x, _: '{:g}'.format(x)))
    p_bias.save(output_path)

    # RMS per channel
    output_path = get_plot(f"d191122_dc_tf/plot_charge_resolution/rms_c.pdf")
    p_bias = ChargePlot()
    for c in range(10):
        rms = std_dc_ext_23[c] / true_dc
        p_bias.plot(true_dc, rms, label=f"{c}")
    p_bias.add_legend('best')
    p_bias.ax.set_xscale('log')
    p_bias.ax.get_xaxis().set_major_formatter(
        FuncFormatter(lambda x, _: '{:g}'.format(x)))
    p_bias.save(output_path)

if __name__ == '__main__':
    main()
