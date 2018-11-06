from CHECLabPySB import HDF5Writer, HDF5Reader
from CHECLabPySB.plotting.setup import Plotter
from CHECLabPySB.scripts.sst_rfi.intensity_resolution import all_files
import numpy as np
import pandas as pd
import os
from numpy.polynomial.polynomial import polyfit
from matplotlib.colors import LogNorm
from matplotlib.ticker import FuncFormatter


class FitPlotter(Plotter):
    def plot(self, x, y, xerr, yerr, flag, c, m, merr):

        x_fit = np.geomspace(0.1, 1000, 20)
        y_fit = m * x_fit + c
        yerr_fit = merr * x_fit

        (_, caps, _) = self.ax.errorbar(x[~flag], y[~flag],
                                        xerr=xerr[~flag], yerr=yerr[~flag],
                                        fmt='o', mew=1, zorder=1,
                                        markersize=3, capsize=3,
                                        elinewidth=0.7, label="")
        for cap in caps:
            cap.set_markeredgewidth(0.7)

        color = self.ax._get_lines.get_next_color()
        # (_, caps, _) = self.ax.errorbar(x_fit, y_fit, yerr=yerr_fit,
        #                                 mew=1, markersize=3, capsize=3,
        #                                 elinewidth=0.7, color=color,
        #                                 label="Linear Regression")
        # for cap in caps:
        #     cap.set_markeredgewidth(0.7)
        self.ax.plot(x_fit, y_fit, color=color,
                     zorder=2, label="Linear Regression")

        (_, caps, _) = self.ax.errorbar(x[flag], y[flag],
                                        xerr=xerr[flag], yerr=yerr[flag],
                                        fmt='o', mew=1, color=color,
                                        markersize=3, capsize=3,
                                        elinewidth=0.7, zorder=1,
                                        label="Regressed Points")
        for cap in caps:
            cap.set_markeredgewidth(0.7)

        t = r"$\gamma_{{M_i}} = \SI[separate-uncertainty = true]{{{:#.2f} \pm {:#.2f}}}{{mVns/\pe}}$"
        self.ax.text(0.5, 0.4, t.format(m, merr), transform=self.ax.transAxes)

        t = "m = {:.2f}, c = {:.2f}"
        self.ax.text(0.5, 0.3, t.format(m, c), transform=self.ax.transAxes)

        self.ax.set_xscale('log')
        self.ax.get_xaxis().set_major_formatter(
            FuncFormatter(lambda xl, _: '{:g}'.format(xl)))

        self.ax.set_yscale('log')
        self.ax.get_yaxis().set_major_formatter(
            FuncFormatter(lambda yl, _: '{:g}'.format(yl)))

        self.ax.set_xlabel("Average Expected Charge (p.e.)")
        self.ax.set_ylabel("Average Measured Charge (mV ns)")
        self.add_legend('best')


class Hist2D(Plotter):
    def plot(self, x, y):
        xbins = np.geomspace(x[x > 0].min(), x.max(), 100)
        ybins = np.geomspace(y[y > 0].min(), y.max(), 100)

        hist, xedges, yedges = np.histogram2d(x.ravel(), y.ravel(),
                                              bins=(xbins, ybins))
        hist = np.ma.masked_where(hist == 0, hist)
        z = hist
        norm = LogNorm(vmin=hist.min(), vmax=hist.max())
        im = self.ax.pcolormesh(xedges, yedges, z.T, cmap="viridis",
                                edgecolors='white', linewidths=0, norm=norm)
        cbar = self.fig.colorbar(im)

        self.ax.set_xscale('log')
        self.ax.get_xaxis().set_major_formatter(
            FuncFormatter(lambda xl, _: '{:g}'.format(xl)))

        self.ax.set_yscale('log')
        self.ax.get_yaxis().set_major_formatter(
            FuncFormatter(lambda yl, _: '{:g}'.format(yl)))

        self.ax.set_xlabel("Average Expected Charge (p.e.)")
        self.ax.set_ylabel("Average Measured Charge (mV ns)")
        cbar.set_label("N")


def process(file):

    charge_averages_path = file.charge_averages_path
    fw_path = file.fw_path
    ff_path = file.ff_path
    plot_dir = file.ff_plot_dir
    poi = file.poi

    with HDF5Reader(charge_averages_path) as reader:
        df_avg = reader.read("data")
        mapping = reader.read_mapping()
        metadata = reader.read_metadata()

    with HDF5Reader(fw_path) as reader:
        df_fw = reader.read("data")
        fw_m = df_fw['fw_m'].values
        fw_merr = df_fw['fw_merr'].values

    pixel = df_avg['pixel'].values
    transmission = df_avg['transmission'].values
    df_avg['illumination'] = transmission * fw_m[pixel]
    df_avg['illumination_err'] = transmission * fw_merr[pixel]

    d_list = []
    for pix in np.unique(df_avg['pixel']):

        df_p = df_avg.loc[df_avg['pixel'] == pix]
        true = df_p['illumination'].values
        true_err = df_p['illumination_err'].values
        measured = df_p['mean'].values
        measured_std = df_p['std'].values

        flag = np.zeros(true.size, dtype=np.bool)
        flag[np.abs(true - 50).argsort()[:3]] = True

        x = true[flag]
        y = measured[flag]
        y_err = measured_std[flag]

        p, f = polyfit(x, y, [1], w=1/y_err, full=True)
        ff_c, ff_m = p

        # n = x.size
        # sy = np.sqrt(np.sum((y - polyval(x, p))**2) / (n - 1))
        # sm = sy * np.sqrt(1/(np.sum((x - np.mean(x))**2)))
        # ff_merr = sm

        ff_merr = 0

        d_list.append(dict(
            pixel=pix,
            ff_c=ff_c,
            ff_m=ff_m,
            ff_merr=ff_merr,
        ))

        if pix == poi:
            print("{:.3f} ± {:.3f}".format(ff_m, ff_merr))
            p_fit = FitPlotter()
            p_fit.plot(true, measured, true_err, measured_std, flag, ff_c, ff_m, ff_merr)
            p_fit.save(os.path.join(plot_dir, "flat_fielding.pdf"))

    df_calib = pd.DataFrame(d_list)
    df_calib = df_calib.sort_values('pixel')
    with HDF5Writer(ff_path) as writer:
        writer.write(data=df_calib)
        writer.write_mapping(mapping)
        writer.write_metadata(**metadata)

    p_hist2d = Hist2D()
    p_hist2d.plot(df_avg['illumination'].values, df_avg['mean'].values)
    p_hist2d.save(os.path.join(plot_dir, "pixel_averages.pdf"))


def main():
    [process(f) for f in all_files]


if __name__ == '__main__':
    main()
