from CHECLabPy.plotting.setup import Plotter
from CHECLabPy.core.io import HDF5Reader, HDF5Writer
from CHECLabPySB import get_data, get_plot
from CHECLabPy.calib.pixel_masks import PixelMasks
from os.path import dirname, abspath, join
import numpy as np
from numpy.polynomial.polynomial import polyfit
import pandas as pd
from matplotlib.ticker import FuncFormatter
from IPython import embed


DIR = abspath(dirname(__file__))


class Image(Plotter):
    def plot(self, x, y, z):

        xp = x[np.nanargmax(z)]
        yp = y[np.nanargmax(z)]
        zp_max = np.nanmax(z)
        zp_min = np.nanmin(z)
        self.ax.plot(xp, yp, 'x', color='black', ms=4)
        self.ax.text(xp+0.5, yp+1, '({}, {})'.format(xp, yp), color='black')
        # levels = np.linspace(0, zp_max, 21)
        levels = np.linspace(zp_min, zp_max, 21)

        nx = np.arange(np.min(x), np.max(x) + 2) - 0.5
        ny = np.arange(np.min(y), np.max(y) + 2) - 0.5
        # counts, xbins, ybins = np.histogram2d(x, y, weights=z, bins=(nx, ny))
        counts, xbins, ybins, image = self.ax.hist2d(x, y, weights=z, bins=(nx, ny))
        image = self.ax.contourf(counts.T, extent=[xbins[0], xbins[-1], ybins[0], ybins[-1]], levels=levels)

        self.fig.colorbar(image, label="Signal-to-Noise")

        # self.ax.minorticks_off()
        # self.ax.xaxis.set_major_locator(MultipleLocator(2))
        # self.ax.yaxis.set_major_locator(MultipleLocator(2))
        self.ax.set_xlabel('Integration-Window Width')
        self.ax.set_ylabel('Integration-Window Shift')


class Curve(Plotter):
    def plot(self, x, y, label):
        sort = np.argsort(x)
        x = x[sort]
        y = y[sort]
        self.ax.plot(x, y, label=label)

    def finish(self):
        self.ax.set_xlabel('Integration-Window Width')
        self.ax.set_ylabel("Signal-to-Noise")


def main():
    path = get_data("d190520_charge_extraction/data/analysis.h5")
    output_dir = get_plot("d190520_charge_extraction/data")

    with HDF5Reader(path) as reader:
        df = reader.read("data")

    extractors = np.unique(df['extractor'])

    peak_extractors = [e for e in extractors if e.startswith("peak")]
    width = np.zeros(len(peak_extractors))
    shift = np.zeros(len(peak_extractors))
    sn_50 = np.zeros(len(peak_extractors))
    sn_3 = np.zeros(len(peak_extractors))
    for iex, extractor in enumerate(peak_extractors):
        width[iex] = int(extractor.split("_")[1])
        shift[iex] = int(extractor.split("_")[2])
        series = df.loc[df['extractor'] == extractor].iloc[0]
        sn_50[iex] = series['sn_on_50']
        sn_3[iex] = series['sn_on_3']

    p_image = Image(sidebyside=True)
    p_image.plot(width, shift, sn_50)
    p_image.ax.set_title("Mid Average Illumination")
    p_image.save(join(output_dir, f"peak_sn_50.pdf"))

    p_image = Image(sidebyside=True)
    p_image.plot(width, shift, sn_3)
    p_image.ax.set_title("Low Average Illumination")
    p_image.save(join(output_dir, f"peak_sn_3.pdf"))

    sliding_extractors = [e for e in extractors if e.startswith("sliding")]
    width = np.zeros(len(sliding_extractors))
    sn_50 = np.zeros(len(sliding_extractors))
    sn_3 = np.zeros(len(sliding_extractors))
    sn_peak_50 = np.zeros(len(sliding_extractors))
    sn_peak_3 = np.zeros(len(sliding_extractors))
    for iex, extractor in enumerate(sliding_extractors):
        width[iex] = int(extractor.split("_")[1])
        series = df.loc[df['extractor'] == extractor].iloc[0]
        sn_50[iex] = series['sn_on_50']
        sn_3[iex] = series['sn_on_3']

        shift = width[iex] // 2
        peak_extractor = f"peak_{width[iex]:.0f}_{shift:.0f}"
        if peak_extractor in extractors:
            series = df.loc[df['extractor'] == peak_extractor].iloc[0]
            sn_peak_50[iex] = series['sn_on_50']
            sn_peak_3[iex] = series['sn_on_3']

    series = df.loc[df['extractor'] == "cc_nn"].iloc[0]
    cc_sn_50 = series['sn_on_50']
    cc_sn_3 = series['sn_on_3']

    p_curve = Curve(sidebyside=True)
    p_curve.plot(width, sn_50, "Sliding Window")
    p_curve.plot(width, sn_peak_50, "Peak Finding")
    p_curve.plot(width, np.full(width.size, cc_sn_50), "Cross Correlation")
    # p_curve.ax.axhline(cc_sn_50, label='Cross Correlation')
    p_curve.add_legend("best")
    p_curve.ax.set_title("Mid Average Illumination")
    p_curve.save(join(output_dir, f"sliding_sn_50.pdf"))

    p_curve = Curve(sidebyside=True)
    p_curve.plot(width, sn_3, "Sliding Window")
    p_curve.plot(width, sn_peak_3, "Peak Finding")
    p_curve.plot(width, np.full(width.size, cc_sn_3), "Cross Correlation")
    # p_curve.ax.axhline(cc_sn_3, label='Cross Correlation')
    p_curve.add_legend("best")
    p_curve.ax.set_title("Low Average Illumination")
    p_curve.save(join(output_dir, f"sliding_sn_3.pdf"))



    #
    #
    # for true, group in df.groupby('true'):
    #     n = group['n'].values[0]
    #     if n < 1000:
    #         continue
    #
    #     x = group['width'].values
    #     y = group['shift'].values
    #     z = group['rmse'].values
    #
    #     m = x > 3
    #     x = x[m]
    #     y = y[m]
    #     z = z[m]
    #
    #     p_image = Image(sidebyside=True)
    #     p_image.plot(x, y, z)
    #     p_image.save(join(output_dir, f"t{true}.pdf"))


if __name__ == '__main__':
    main()