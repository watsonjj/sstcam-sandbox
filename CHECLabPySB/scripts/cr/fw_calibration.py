from CHECLabPySB.plotting.setup import Plotter
from CHECLabPySB import HDF5Writer, HDF5Reader
from CHECLabPySB.scripts.cr import all_files
import numpy as np
import pandas as pd
import re
from CHECLabPy.utils.files import open_runlist_dl1
from numpy.polynomial.polynomial import polyfit, polyval
import seaborn as sns
import os
from matplotlib.ticker import FuncFormatter
import warnings
from IPython import embed


class FitPlotter(Plotter):
    def plot(self, x, y, yerr, c, m):


        # color = self.ax._get_lines.get_next_color()

        for i in range(y.shape[1]):
            xf = np.linspace(x.min(), x.max(), 2)
            yf = polyval(xf, (c[i], m[i]))

            color = self.ax._get_lines.get_next_color()

            (_, caps, _) = self.ax.errorbar(x, y[:, i], yerr=yerr[:, i],
                                            fmt='x', mew=1, color=color,
                                            markersize=3, capsize=3,
                                            elinewidth=0.7,
                                            label="Pixel {}".format(i))
            for cap in caps:
                cap.set_markeredgewidth(0.7)

            # self.ax.plot(x, y[:, i], 'x', color=color)
            self.ax.plot(xf, yf, color=color, label="")

        self.ax.set_xticks(x)
        self.ax.tick_params(axis='x', which='minor', bottom=False, top=False)

        self.ax.set_xlabel("Filter-Wheel Transmission")
        self.ax.set_ylabel(r"$\lambda$ (p.e.)")

        self.add_legend('best')


class LinePlotter(Plotter):
    def plot(self, m_avg, m_pix, m_avg_std):
        x = np.geomspace(0.0001, 1, 20)
        y_avg = x * m_avg
        y_avg_err = x * m_avg_std
        y_pix = x[:, None] * m_pix[None, :]

        imax = np.argmax(m_pix)
        imin = np.argmin(m_pix)

        color = next(self.ax._get_lines.prop_cycler)['color']
        # self.ax.fill_between(x, y_pix[:, imin], y_pix[:, imax],
        #                      facecolor=color, edgecolor=color,
        #                      label="Range for True Pixel Positions")

        (_, caps, _) = self.ax.errorbar(x, y_avg, yerr=y_avg_err,
                                        mew=1, color='black',
                                        markersize=3, capsize=3,
                                        elinewidth=0.7,
                                        label="Pixel at Camera Centre")
        for cap in caps:
            cap.set_markeredgewidth(0.7)
        # self.ax.plot(x, y_avg, color='black',
        #              label="Pixel at Camera Centre")


        t = r"$\average{{M}}_\lambda = \SI[separate-uncertainty = true]{{{:#.2f} \pm {:#.2f}}}{{\pe}}$"
        self.ax.text(0.5, 0.4, t.format(m_avg, m_avg_std), transform=self.ax.transAxes)

        self.ax.set_xscale('log')
        self.ax.get_xaxis().set_major_formatter(
            FuncFormatter(lambda x, _: '{:g}'.format(x)))
        self.ax.set_yscale('log')
        self.ax.get_yaxis().set_major_formatter(
            FuncFormatter(lambda x, _: '{:g}'.format(x)))


        self.ax.set_xlabel("Filter-Wheel Transmission")
        self.ax.set_ylabel("Average Expected Charge (p.e.)")
        self.add_legend('best')


class HistPlotter(Plotter):
    def plot(self, m_corrected):
        rel_pde = m_corrected / m_corrected.mean()
        std = np.std(rel_pde)

        label = ("Standard Deviation: {:.3f}".format(std))

        sns.distplot(rel_pde, ax=self.ax, hist=True, kde=False,
                     kde_kws={'shade': True, 'linewidth': 3},
                     label=label, norm_hist=False)

        self.ax.set_xlabel("Relative Photon Detection "
                           "Efficiency Between Pixels")
        self.ax.set_ylabel("Count")
        self.add_legend('best')


def process(file):

    runlist_path = file.spe_runlist_path
    spe_path = file.spe_path
    profile_path = file.illumination_profile_path
    dead = file.dead
    fw_path = file.fw_path
    plot_dir = file.fw_plot_dir

    df_runs = open_runlist_dl1(runlist_path, False)
    df_runs['transmission'] = 1/df_runs['fw_atten']

    store_spe = pd.HDFStore(spe_path)
    df_spe = store_spe['coeff_pixel']
    df_spe_err = store_spe['errors_pixel']
    mapping = store_spe['mapping']
    with warnings.catch_warnings():
        warnings.simplefilter('ignore', UserWarning)
        mapping.metadata = store_spe.get_storer('mapping').attrs.metadata

    meta_spe = store_spe.get_storer('metadata').attrs.metadata
    n_spe_illuminations = meta_spe['n_illuminations']
    spe_files = meta_spe['files']
    n_pixels = meta_spe['n_pixels']

    spe_transmission = []
    pattern = '(.+?)/Run(.+?)_dl1.h5'
    for path in spe_files:
        try:
            reg_exp = re.search(pattern, path)
            if reg_exp:
                run = int(reg_exp.group(2))
                spe_transmission.append(df_runs.loc[run]['transmission'])
        except AttributeError:
            print("Problem with Regular Expression, "
                  "{} does not match patten {}".format(path, pattern))

    pix_lambda = np.zeros((n_spe_illuminations, n_pixels))
    pix_lambda_err = np.zeros((n_spe_illuminations, n_pixels))
    for ill in range(n_spe_illuminations):
        key = "lambda_" + str(ill)
        lambda_ = df_spe[['pixel', key]].sort_values('pixel')[key].values
        lambda_err = df_spe_err[['pixel', key]].sort_values('pixel')[key].values
        pix_lambda[ill] = lambda_
        pix_lambda_err[ill] = lambda_err

    if profile_path:
        with HDF5Reader(profile_path) as reader:
            correction = reader.read("correction")['correction']
    else:
        correction = np.ones(n_pixels)

    df_list = []
    for i in range(n_spe_illuminations):
        df_list.append(pd.DataFrame(dict(
            pixel=np.arange(n_pixels),
            correction=correction,
            transmission=spe_transmission[i],
            lambda_=pix_lambda[i],
            lambda_err=pix_lambda_err[i],
        )))
    df = pd.concat(df_list)

    # Obtain calibration
    dead_mask = np.zeros(n_pixels, dtype=np.bool)
    dead_mask[dead] = True

    transmission = np.unique(df['transmission'].values)
    lambda_ = []
    lambda_err = []
    corrections = []
    for i in range(len(transmission)):
        df_t = df.loc[df['transmission'] == transmission[i]]
        lambda_.append(df_t['lambda_'].values)
        lambda_err.append(df_t['lambda_err'].values)
        corrections.append(df_t['correction'].values)
    correction = corrections[0]
    lambda_ = np.array(lambda_)
    lambda_err = np.array(lambda_err)

    c_list = []
    m_list = []
    merr_list = []
    for pix in range(n_pixels):
        x = transmission
        y = lambda_[:, pix]
        yerr = lambda_err[:, pix]
        w = 1/yerr
        cp, mp = polyfit(x, y, 1, w=w)
        c_list.append(cp)
        m_list.append(mp)

        w2 = w**2
        merrp = np.sqrt(np.sum(w2)/(np.sum(w2)*np.sum(w2*x**2) - (np.sum(w2*x))**2))
        merr_list.append(merrp)

    c = np.array(c_list)
    m = np.array(m_list)
    merr = np.array(merr_list)

    # Exlude low gradients (dead pixels)
    # dead_mask[m < 1000] = True

    merr_corrected = merr / correction
    merr_corrected_d = merr_corrected[~dead_mask]

    m_corrected = m / correction
    m_corrected_d = m_corrected[~dead_mask]
    w = 1/merr_corrected_d
    m_avg = np.average(m_corrected_d, weights=w)
    m_pix = m_avg * correction
    m_avg_std = np.sqrt(np.average((m_corrected_d - m_avg) ** 2, weights=w))
    m_pix_std = m_avg_std * correction

    print("{:.3f} ± {:.3f}".format(m_avg, m_avg_std))

    df_calib = pd.DataFrame(dict(
        pixel=np.arange(n_pixels),
        fw_m=m_pix,
        fw_merr=m_pix_std,
    ))
    df_calib = df_calib.sort_values('pixel')

    with HDF5Writer(fw_path) as writer:
        writer.write(data=df_calib)
        writer.write_mapping(mapping)
        writer.write_metadata(
            n_pixels=n_pixels,
            fw_m_camera=m_avg,
            fw_merr_camera=m_avg_std,
        )

    p_fit = FitPlotter()
    l = np.s_[:5]
    p_fit.plot(transmission, lambda_[:, l], lambda_err[:, l], c[l], m[l])
    p_fit.save(os.path.join(plot_dir, "fw_calibration_fit.pdf"))

    p_line = LinePlotter()
    p_line.plot(m_avg, m_pix, m_avg_std)
    p_line.save(os.path.join(plot_dir, "fw_calibration.pdf"))

    p_hist = HistPlotter()
    p_hist.plot(m_corrected[~dead_mask])
    p_hist.save(os.path.join(plot_dir, "relative_pde.pdf"))


def main():
    [process(f) for f in all_files]


if __name__ == '__main__':
    main()
