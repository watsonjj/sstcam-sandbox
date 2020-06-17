from CHECLabPy.plotting.setup import Plotter
from sstcam_sandbox.d190313_spectra_fitting import *
from sstcam_sandbox import get_plot
from CHECLabPy.core.io import DL1Reader
from sstcam_sandbox.d190313_spectra_fitting.gentile_old import GentileFitterOld
from sstcam_sandbox.d190313_spectra_fitting.gentile_new import GentileFitterNew
from matplotlib import pyplot as plt
import os
import numpy as np


class SPEPlotter(Plotter):
    def plot(self, fitx, fitter):
        color = next(self.ax._get_lines.prop_cycler)['color']

        edges = fitter.edges
        between = fitter.between
        n_illuminations = fitter.n_illuminations
        coeff = fitter.coeff
        errors = fitter.errors
        for i in range(n_illuminations):
            lambda_ = coeff['lambda_{}'.format(i)]
            lambda_err = errors['lambda_{}'.format(i)]
            hist = fitter.hist[i]
            fit = fitter.fit_function(fitx, **coeff)[i]

            self.ax.hist(between, bins=edges, weights=hist, histtype='step',
                         color=color)
            self.ax.plot(fitx, fit, color=color,
                         label=f"{lambda_:.3f} ± {lambda_err:.3f} p.e.")

        self.add_legend()
        self.ax.set_xlabel("Charge (mV ns)")
        self.ax.set_ylabel("N")


class SPEPlotterTable(SPEPlotter):
    def __init__(self):
        super().__init__()

        self.fig = plt.figure(figsize=self.get_figsize())
        self.ax = plt.subplot2grid((3, 2), (0, 0), rowspan=3)
        self.ax_t = plt.subplot2grid((3, 2), (0, 1), rowspan=3)

    def plot(self, fitx, fitter):
        super().plot(fitx, fitter)

        coeff = fitter.coeff
        errors = fitter.errors

        self.ax_t.axis('off')
        columns = ['Fit Coeff', 'Fit Errors']
        rows = list(coeff.keys())
        cells = [['%.3g' % coeff[i], '%.3g' % errors[i]] for i in rows]
        table = self.ax_t.table(cellText=cells, rowLabels=rows,
                                colLabels=columns, loc='center')
        table.set_fontsize(10)


def process(file, fitter_class):
    name = file.__class__.__name__
    input_paths = file.dl1_paths
    spe_config = file.spe_config
    poi = file.poi
    output_dir = get_plot(f"d190313_spectra_fitting/{name}")
    fitter_class_name = fitter_class.__name__

    readers = [DL1Reader(path) for path in input_paths]
    n_illuminations = len(readers)
    fitter = fitter_class(n_illuminations, spe_config)

    charges = []
    for reader in readers:
        pixel, charge = reader.select_columns(['pixel', 'charge_cc'])
        if poi != -1:
            charge_p = charge[pixel == poi]
        else:
            charge_p = charge
        charges.append(charge_p)
    fitter.apply(*charges)

    fitx = np.linspace(fitter.range[0], fitter.range[1], 1000)

    p_spe = SPEPlotter()
    p_spe.plot(fitx, fitter)
    p_spe.save(os.path.join(output_dir, f"fit_{fitter_class_name}.pdf"))

    p_spe_table = SPEPlotterTable()
    p_spe_table.plot(fitx, fitter)
    p_spe_table.save(os.path.join(output_dir, f"fit_table_{fitter_class_name}.pdf"))


def main():
    datasets = [
        MC(),
    ]
    fitters = [
        GentileFitterOld,
        GentileFitterNew,
    ]
    for ids, ds in enumerate(datasets):
        print(f"----DATASET: {ids}/{len(datasets)}")
        for f in fitters:
            process(ds, f)


if __name__ == '__main__':
    main()
