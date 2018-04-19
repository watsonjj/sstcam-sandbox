import argparse
from argparse import ArgumentDefaultsHelpFormatter as Formatter
import numpy as np
import pandas as pd
import os
import warnings

from matplotlib.ticker import FuncFormatter

from CHECLabPy.plotting.waveform import WaveformPlotter
from CHECLabPy.plotting.setup import Plotter
from CHECLabPy.waveform_reducers.cross_correlation import CrossCorrelation
from IPython import embed


class Scatter(Plotter):
    def __init__(self, x_label="", y_label=""):
        super().__init__()
        self.x_label = x_label
        self.y_label = y_label

    def add(self, x, y, x_err=None, y_err=None, label='', c=None, fmt='o', **kwargs):
        if not c:
            c = self.ax._get_lines.get_next_color()
        (_, caps, _) = self.ax.errorbar(x, y, xerr=x_err, yerr=y_err, fmt=fmt, mew=1, color=c, alpha=1, markersize=3, capsize=3, elinewidth=0.7, label=label, **kwargs)

        for cap in caps:
            cap.set_markeredgewidth(0.7)

    def add_saturation_region(self, x1, x2):
        self.ax.axvspan(x1, x2, color='red', alpha=0.5, ec=None)

    def set_log_x(self):
        self.ax.set_xscale('log')
        self.ax.get_xaxis().set_major_formatter(
            FuncFormatter(lambda x, _: '{:g}'.format(x)))

    def set_log_y(self):
        self.ax.set_yscale('log')
        self.ax.get_yaxis().set_major_formatter(
            FuncFormatter(lambda y, _: '{:g}'.format(y)))

    def finish(self):
        self.ax.set_xlabel(self.x_label)
        self.ax.set_ylabel(self.y_label)



def main():

    store = pd.HDFStore("/Users/Jason/Software/CHECLabPy_sandbox/rich/rich.h5")

    mapping = store['mapping']
    with warnings.catch_warnings():
        warnings.simplefilter('ignore', UserWarning)
        mapping.metadata = store.get_storer('mapping').attrs.metadata

    df = store['mean']
    df = df[['pixel', 'charge', 'amplitude', 'attenuation', 'fwhm', 'tr', 'saturation_coeff']]
    i50 = np.argmin(np.abs(np.unique(df['amplitude'].values) - 50))
    amp50 = np.unique(df['amplitude'].values)[i50]
    df_50 = df.loc[df['amplitude'] == amp50]
    dead_mask = df_50['charge'] < 0.8 * df_50['charge'].mean()
    dead = df_50['pixel'][dead_mask].values
    df = df[~df.pixel.isin(dead)]

    # df = df.loc[df['amplitude'] > 200]
    embed()
    df = df.loc[(df['fwhm'] < 15) & (df['fwhm'] > 0)]
    df = df.loc[(df['tr'] < 15) & (df['tr'] > 0)]

    # embed()

    df_mean = df.groupby('amplitude').mean().reset_index()
    df_std = df.groupby('amplitude').apply(np.std)#.reset_index()

    output_dir = "/Users/Jason/Software/CHECLabPy_sandbox/rich"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print("Created directory: {}".format(output_dir))

    p_charge = Scatter("Illumination (p.e.)", "Charge (mV ns)")
    x = df_mean['amplitude'].values
    y = df_mean['charge'].values
    dy = df_std['charge'].values
    p_charge.add(x, y, None, dy)
    p_charge.set_log_x()
    p_charge.set_log_y()
    p_charge.save(os.path.join(output_dir, "charge.pdf"))

    p_fwhm = Scatter("Illumination (p.e.)", "FWHM (ns)")
    x = df_mean['amplitude'].values
    y = df_mean['fwhm'].values
    dy = df_std['fwhm'].values
    p_fwhm.add(x, y, None, dy)
    p_fwhm.set_log_x()
    p_fwhm.save(os.path.join(output_dir, "fwhm.pdf"))

    p_tr = Scatter("Illumination (p.e.)", "Rise Time (ns)")
    x = df_mean['amplitude'].values
    y = df_mean['tr'].values
    dy = df_std['tr'].values
    p_tr.add(x, y, None, dy)
    p_tr.set_log_x()
    p_tr.save(os.path.join(output_dir, "tr.pdf"))

    p_sat = Scatter("Illumination (p.e.)", "Saturation Coefficient (mV ns)")
    x = df_mean['amplitude'].values
    y = df_mean['saturation_coeff'].values
    dy = df_std['saturation_coeff'].values
    p_sat.add(x, y, None, dy)
    p_sat.set_log_x()
    p_sat.set_log_y()
    p_sat.save(os.path.join(output_dir, "satcoeff.pdf"))



if __name__ == '__main__':
    main()