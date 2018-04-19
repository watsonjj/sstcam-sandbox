import argparse
from argparse import ArgumentDefaultsHelpFormatter as Formatter
import numpy as np
import pandas as pd
import os
import warnings

from matplotlib.ticker import FuncFormatter

from CHECLabPy.core.io import DL1Reader
from CHECLabPy.plotting.waveform import WaveformPlotter
from CHECLabPy.plotting.setup import Plotter
from CHECLabPy.waveform_reducers.cross_correlation import CrossCorrelation
from IPython import embed


class Hist(Plotter):
    def __init__(self, x_label="", y_label=""):
        super().__init__()
        self.x_label = x_label
        self.y_label = y_label

    def plot(self, data, bins=None, range_=None, label="", color=None, alpha=None):
        self.ax.hist(data, bins=bins, range=range_,
                     histtype='step', normed=True, label=label,
                     color=color, alpha=alpha)

    def finish(self):
        self.ax.set_xlabel(self.x_label)
        self.ax.set_ylabel(self.y_label)


def main():
    reader = DL1Reader("/Volumes/gct-jason/dynamicrange/Run17493_dl1.h5")

    poi1 = 0
    poi2 = 346
    poi3 = 1564

    pixel, charge = reader.select_columns(['pixel', 'charge'])
    pixel_mask1 = pixel == poi1
    charge_pix1 = charge[pixel_mask1]
    pixel_mask2 = pixel == poi2
    charge_pix2 = charge[pixel_mask2]
    pixel_mask3 = pixel == poi3
    charge_pix3 = charge[pixel_mask3]

    output_dir = os.path.abspath(os.path.dirname(__file__))
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print("Created directory: {}".format(output_dir))

    p_hist = Hist("Charge (mV ns)", "Normalised Density")
    # p_hist.plot(charge_pix1, bins=100, range_=[-30, 100], label="Pixel {}".format(poi1))
    p_hist.plot(charge_pix2, bins=100, range_=[-30, 100], label="Pixel {}".format(poi2))
    # p_hist.plot(charge_pix3, bins=100, range_=[-30, 100], label="Pixel {}".format(poi3))
    p_hist.plot(charge, bins=100, range_=[-30, 100], label="Camera", color='black')
    p_hist.add_legend()
    p_hist.save(os.path.join(output_dir, "camera.pdf"))


if __name__ == '__main__':
    main()