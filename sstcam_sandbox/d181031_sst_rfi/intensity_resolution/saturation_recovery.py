from sstcam_sandbox.plotting.setup import Plotter
from sstcam_sandbox import HDF5Writer, HDF5Reader
from sstcam_sandbox.d181031_sst_rfi.intensity_resolution import all_files
import pandas as pd
from tqdm import tqdm
from CHECLabPy.utils.files import open_runlist_dl1
from CHECLabPy.utils.resolutions import ChargeStatistics
import numpy as np
from numpy.polynomial.polynomial import polyfit, polyval
from matplotlib.colors import LogNorm
from matplotlib.ticker import FuncFormatter


class FitPlotter(Plotter):
    def plot(self, x, y, xerr, yerr, flag, p):

        x_fit = np.geomspace(0.1, 10000, 20)
        y_fit = polyval(x_fit, p)

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

        # t = r"$\gamma_{{M_i}} = \SI[separate-uncertainty = true]{{{:#.2f} \pm {:#.2f}}}{{mVns/\pe}}$"
        # self.ax.text(0.5, 0.4, t.format(m, merr), transform=self.ax.transAxes)
        #
        # t = "m = {:.2f}, c = {:.2f}"
        # self.ax.text(0.5, 0.3, t.format(m, c), transform=self.ax.transAxes)

        self.ax.set_xscale('log')
        self.ax.get_xaxis().set_major_formatter(
            FuncFormatter(lambda xl, _: '{:g}'.format(xl)))

        self.ax.set_yscale('log')
        self.ax.get_yaxis().set_major_formatter(
            FuncFormatter(lambda yl, _: '{:g}'.format(yl)))

        self.ax.set_xlabel("Average Expected Charge (p.e.)")
        self.ax.set_ylabel("Average Measured Charge (mV ns)")
        self.add_legend('best')


def process(file):
    runlist_path = file.runlist_path
    output_path = file.saturation_recovery_path
    fw_path = file.fw_path
    plot_path = file.saturation_recovery_plot_path
    poi = file.poi

    df_runs = open_runlist_dl1(runlist_path)
    df_runs['transmission'] = 1/df_runs['fw_atten']
    n_runs = df_runs.index.size
    mapping = df_runs.iloc[0]['reader'].mapping
    n_pixels = df_runs.iloc[0]['reader'].n_pixels

    cs = ChargeStatistics()

    desc0 = "Looping over files"
    it = enumerate(df_runs.iterrows())
    for i, (_, row) in tqdm(it, total=n_runs, desc=desc0):
        reader = row['reader']
        transmission = row['transmission']
        n_rows = n_pixels * 1000
        pixel, charge = reader.select_columns(['pixel', 'saturation_coeff'], stop=n_rows)
        cs.add(pixel, transmission, charge)
        reader.store.close()
    df_pixel, df_camera = cs.finish()

    df = df_pixel[["pixel", "amplitude", "mean", "std"]].copy()
    df = df.rename(columns={"amplitude": "transmission"})
    df_runs2 = df_runs[['transmission', 'pe_expected', 'fw_pos']].copy()
    df_runs2['run_number'] = df_runs2.index
    df = pd.merge(df, df_runs2, on='transmission')

    with HDF5Reader(fw_path) as reader:
        df_fw = reader.read("data")
        fw_m = df_fw['fw_m'].values
        fw_merr = df_fw['fw_merr'].values

    pixel = df['pixel'].values
    transmission = df['transmission'].values
    df['illumination'] = transmission * fw_m[pixel]
    df['illumination_err'] = transmission * fw_merr[pixel]

    d_list = []
    for pix in np.unique(df['pixel']):

        df_p = df.loc[df['pixel'] == pix]
        true = df_p['illumination'].values
        true_err = df_p['illumination_err'].values
        measured = df_p['mean'].values
        measured_std = df_p['std'].values

        flag = np.zeros(true.size, dtype=np.bool)
        flag[np.abs(true - 2500).argsort()[:5]] = True

        x = true[flag]
        y = measured[flag]
        y_err = measured_std[flag]

        p = polyfit(x, y, [1], w=1/y_err)
        ff_c, ff_m = p

        d_list.append(dict(
            pixel=pix,
            ff_c=ff_c,
            ff_m=ff_m,
        ))

        if pix == poi:
            print("{:.3f}".format(ff_m))
            p_fit = FitPlotter()
            p_fit.plot(true, measured, true_err, measured_std, flag, p)
            p_fit.save(plot_path)

    df_calib = pd.DataFrame(d_list)
    df_calib = df_calib.sort_values('pixel')
    with HDF5Writer(output_path) as writer:
        writer.write(data=df_calib)
        writer.write_mapping(mapping)
        writer.write_metadata(n_pixels=n_pixels)


def main():
    [process(f) for f in all_files]


if __name__ == '__main__':
    main()
