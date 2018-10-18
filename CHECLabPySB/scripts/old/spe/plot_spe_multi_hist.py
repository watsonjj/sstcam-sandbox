"""
Executable for extracting the Single-Photoelectron spectrum and fit from dl1
files
"""
import os
import argparse
from argparse import ArgumentDefaultsHelpFormatter as Formatter
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
        coeff = fitter.coeff.copy()

        for i in range(fitter.n_illuminations):
            color = next(self.ax._get_lines.prop_cycler)['color']
            lambda_ = coeff['lambda_{}'.format(i)]
            hist = fitter.hist[i]
            edges = fitter.edges
            between = fitter.between
            fit = fitter.fit_function(x, **coeff)[i]

            self.ax.hist(between, bins=edges, weights=hist, histtype='step',
                         color=color)
            self.ax.plot(x, fit, color=color,
                         label="{:.3f} p.e.".format(lambda_))

        self.ax.legend(loc=1, frameon=True, fancybox=True, framealpha=0.7)
        self.ax_t.axis('off')
        columns = ['Fit Coeff']
        rows = list(coeff.keys())
        cells = [['%.3g' % coeff[i]] for i in rows]
        table = self.ax_t.table(cellText=cells, rowLabels=rows,
                                colLabels=columns, loc='center')
        table.set_fontsize(10)


def main():
    description = ('Extract and fit the Single-Photoelectron spectrum '
                   'from N dl1 files simultaneously')
    parser = argparse.ArgumentParser(description=description,
                                     formatter_class=Formatter)
    parser.add_argument('-f', '--files', dest='input_paths', nargs='+',
                        help='path to the input dl1 run files')
    parser.add_argument('-o', '--output', dest='output_path', action='store',
                        required=True, help='path to store the output image')
    parser.add_argument('-s', '--fitter', dest='fitter', action='store',
                        default='GentileFitter',
                        choices=SpectrumFitterFactory.subclass_names,
                        help='SpectrumFitter to use')
    parser.add_argument('-c', '--config', dest='config', action='store',
                        default=None,
                        help='Path to SpectrumFitter configuration YAML file')
    parser.add_argument('-p', '--pixel', dest='plot_pixel', action='store',
                        default=None, type=int,
                        help='Pixel to plot. "-1" speciefies the '
                             'entire camera')
    args = parser.parse_args()

    input_paths = args.input_paths
    output_path = args.output_path
    fitter_str = args.fitter
    config_path = args.config
    poi = args.plot_pixel

    readers = [DL1Reader(path) for path in input_paths]
    kwargs = dict(
        product_name=fitter_str,
        n_illuminations=len(readers),
        config_path=config_path
    )
    fitter = SpectrumFitterFactory.produce(**kwargs)

    output_dir = os.path.dirname(output_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print("Created directory: {}".format(output_dir))
    if os.path.exists(output_path):
        os.remove(output_path)

    charges = []
    for reader in readers:
        pixel, charge = reader.select_columns(['pixel', 'charge'])
        if poi != -1:
            charge_p = charge[pixel == poi]
        else:
            charge_p = charge
        charges.append(charge_p)
    fitter.apply(*charges)

    p_data = SPEPlotter()
    p_data.plot(fitter)
    p_data.save(output_path)


if __name__ == '__main__':
    main()
