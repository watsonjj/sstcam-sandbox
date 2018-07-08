"""
Executable for extracting the Single-Photoelectron spectrum and fit from dl1
files
"""
import numpy as np
from matplotlib import pyplot as plt
from CHECLabPy.core.io import DL1Reader
from CHECLabPy.core.factory import SpectrumFitterFactory
from CHECLabPy.plotting.setup import Plotter
from CHECLabPy.spectrum_fitters.gentile import GentileFitter


class SPEPlotter(Plotter):
    def __init__(self, talk=False):
        super().__init__(talk=talk)
        self.fig = plt.figure(figsize=(13, 6))
        self.ax = plt.subplot2grid((3, 2), (0, 0), rowspan=3)
        self.ax_t = plt.subplot2grid((3, 2), (0, 1), rowspan=3)

    def plot(self, fitter):
        x = np.linspace(fitter.range[0], fitter.range[1], 1000)

        coeff_initial = fitter.p0.copy()
        initial = fitter.get_fit_summed(x, **coeff_initial)

        hist = fitter.hist[0]
        edges = fitter.edges
        between = fitter.between

        coeff = fitter.coeff.copy()
        fit = fitter.get_fit_summed(x, **coeff)

        self.ax.plot(x, initial, label="Initial")
        self.ax.hist(between, bins=edges, weights=hist, histtype='step',
                     label="Hist")
        self.ax.plot(x, fit, label="Fit")
        self.ax.legend(loc=1, frameon=True, fancybox=True, framealpha=0.7)
        self.ax_t.axis('off')
        columns = ['Initial', 'Fit']
        rows = list(coeff.keys())
        cells = [['%.3g' % coeff_initial[i], '%.3g' % coeff[i]] for i in rows]
        table = self.ax_t.table(cellText=cells, rowLabels=rows,
                                colLabels=columns, loc='center')
        table.set_fontsize(6)


class SPEPlotterMulti(Plotter):
    def __init__(self, talk=False):
        super().__init__(talk=talk)
        self.fig = plt.figure(figsize=(13, 6))
        self.ax = plt.subplot2grid((3, 2), (0, 0), rowspan=3)
        self.ax_t = plt.subplot2grid((3, 2), (0, 1), rowspan=3)

    def plot(self, data_fitter, mc_fitter):
        x = np.linspace(data_fitter.range[0], data_fitter.range[1], 1000)

        coeff_initial = data_fitter.p0.copy()
        initial_norm = coeff_initial['norm0']
        initial = data_fitter.get_fit_summed(x, **coeff_initial) / initial_norm

        data_coeff = data_fitter.coeff.copy()
        data_norm = data_coeff['norm0']
        data_hist = data_fitter.hist[0] / data_norm
        data_edges = data_fitter.edges
        data_between = data_fitter.between
        data_fit = data_fitter.get_fit_summed(x, **data_coeff) / data_norm

        mc_coeff = mc_fitter.coeff.copy()
        mc_norm = mc_coeff['norm0']
        mc_hist = mc_fitter.hist[0] / mc_norm
        mc_edges = mc_fitter.edges
        mc_between = mc_fitter.between
        mc_fit = mc_fitter.get_fit_summed(x, **mc_coeff) / mc_norm

        self.ax.plot(x, initial, label="Initial")
        self.ax.hist(data_between, bins=data_edges, weights=data_hist,
                     histtype='step', label="Data Hist")
        self.ax.hist(mc_between, bins=mc_edges, weights=mc_hist,
                     histtype='step', label="MC Hist")
        self.ax.plot(x, data_fit, label="Data Fit")
        self.ax.plot(x, mc_fit, label="MC Fit")
        self.ax.legend(loc=1, frameon=True, fancybox=True, framealpha=0.7)
        self.ax_t.axis('off')
        columns = ['Initial', 'Data Fit', 'MC Fit']
        rows = list(data_coeff.keys())
        cells = [['%.3g' % coeff_initial[i], '%.3g' % data_coeff[i], '%.3g' % mc_coeff[i]] for i in rows]
        table = self.ax_t.table(cellText=cells, rowLabels=rows,
                                colLabels=columns, loc='center')
        table.set_fontsize(6)



def main():
    poi = 2000

    data_path = "/Users/Jason/Software/CHECLabPy_sandbox/mc_config/spe_spectrum_fix/Run43516_dl1.h5"
    data_reader = DL1Reader(data_path)
    data_pixel, data_charge = data_reader.select_columns(['pixel', 'cc_height'])
    data_charge_p = data_charge[data_pixel == poi]
    data_fitter = GentileFitter(1)

    data_fitter.range = [-2, 20]
    data_fitter.range = [-2, 20]
    data_fitter.initial['eped_sigma'] = 0.5
    data_fitter.initial['spe'] = 2.5
    data_fitter.initial['spe_sigma'] = 0.5
    data_fitter.limits['limit_eped_sigma'] = [0.001, 1]
    data_fitter.limits['limit_spe'] = [0.001, 5]
    data_fitter.limits['limit_spe_sigma'] = [0.001, 1]

    data_fitter.apply(data_charge_p)
    data_eped = data_fitter.coeff['eped']
    data_spe = data_fitter.coeff['spe']
    data_charge_norm = (data_charge_p - data_eped) / data_spe

    mc_path = "/Users/Jason/Software/CHECLabPy_sandbox/mc_config/spe_spectrum_fix/run43516_new_spectrum_r0.hd5"
    mc_reader = DL1Reader(mc_path)
    mc_pixel, mc_charge = mc_reader.select_columns(['pixel', 'cc_height'])
    mc_charge_p = mc_charge[mc_pixel == poi]
    mc_fitter = GentileFitter(1)

    mc_fitter.range = [-2, 20]
    mc_fitter.initial['eped_sigma'] = 0.5
    mc_fitter.initial['spe'] = 2.5
    mc_fitter.initial['spe_sigma'] = 0.5
    mc_fitter.limits['limit_eped_sigma'] = [0.001, 1]
    mc_fitter.limits['limit_spe'] = [0.001, 5]
    mc_fitter.limits['limit_spe_sigma'] = [0.001, 1]

    # mc_fitter.range = [-0.5, 4]
    # mc_fitter.initial['eped_sigma'] = 0.1
    # mc_fitter.initial['spe'] = 0.4
    # mc_fitter.initial['spe_sigma'] = 0.05
    # mc_fitter.limits['limit_eped_sigma'] = [0.001, 1]
    # mc_fitter.limits['limit_spe'] = [0.001, 2]
    # mc_fitter.limits['limit_spe_sigma'] = [0.001, 1]

    mc_fitter.apply(mc_charge_p)
    mc_eped = mc_fitter.coeff['eped']
    mc_spe = mc_fitter.coeff['spe']
    mc_charge_norm = (mc_charge_p - mc_eped) / mc_spe

    data_norm_fitter = GentileFitter(1)
    data_norm_fitter.range = [-2, 4]
    data_norm_fitter.initial['eped_sigma'] = 0.5
    data_norm_fitter.initial['spe'] = 1
    data_norm_fitter.initial['spe_sigma'] = 0.1
    data_norm_fitter.limits['limit_eped_sigma'] = [0.001, 1]
    data_norm_fitter.limits['limit_spe'] = [0.001, 2]
    data_norm_fitter.limits['limit_spe_sigma'] = [0.001, 1]
    data_norm_fitter.apply(data_charge_norm)

    mc_norm_fitter = GentileFitter(1)
    mc_norm_fitter.range = [-2, 4]
    mc_norm_fitter.initial['eped_sigma'] = 0.1
    mc_norm_fitter.initial['spe'] = 1
    mc_norm_fitter.initial['spe_sigma'] = 0.05
    mc_norm_fitter.limits['limit_eped_sigma'] = [0.001, 1]
    mc_norm_fitter.limits['limit_spe'] = [0.001, 2]
    mc_norm_fitter.limits['limit_spe_sigma'] = [0.001, 1]
    mc_norm_fitter.apply(mc_charge_norm)

    p_data = SPEPlotter()
    p_data.plot(data_fitter)
    p_data.save("fit_data.pdf")

    p_mc = SPEPlotter()
    p_mc.plot(mc_fitter)
    p_mc.save("fit_mc.pdf")

    p_comparison = SPEPlotterMulti()
    p_comparison.plot(data_norm_fitter, mc_norm_fitter)
    p_comparison.save("fit_comparison.pdf")


if __name__ == '__main__':
    main()
