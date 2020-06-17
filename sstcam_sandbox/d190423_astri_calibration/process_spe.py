from sstcam_sandbox import get_astri_2019
from os.path import join
import re
from glob import glob
import numpy as np
import pandas as pd
from CHECLabPy.calib import PixelMasks
from CHECLabPy.plotting.setup import Plotter
from matplotlib.ticker import MultipleLocator
from numpy.polynomial.polynomial import polyfit, polyval


DATA = get_astri_2019("d2019-04-23_nudges")
RESULTS = join(DATA, "results/process_spe")


class CCVsLambda(Plotter):
    def plot(self, cc, lambda_, lambda_error, ped, cc2pe):
        (_, caps, _) = self.ax.errorbar(
            lambda_, cc, xerr=lambda_error, mew=1, capsize=1,
            elinewidth=0.5, markersize=2, linewidth=0.5, fmt='.'
        )
        for cap in caps:
            cap.set_markeredgewidth(0.5)
        x = np.linspace(lambda_.min(), lambda_.max(), 100)
        label = f"y = {cc2pe:.3f}x + {ped:.3f}"
        self.ax.plot(
            x, polyval(x, [ped, cc2pe]), '--', alpha=0.7, label=label
        )

        self.ax.set_xlabel("Lambda (p.e.)")
        self.ax.set_ylabel("Cross Correlated Charge (mVns)")
        self.add_legend("upper left")


class ParamPlotter(Plotter):
    def __init__(self, y_label):
        super().__init__()
        self.y_label = y_label

    def plot(self, nudge, value, value_err, coeff=None):
        (_, caps, _) = self.ax.errorbar(
            nudge, value, yerr=value_err, mew=1, capsize=1,
            elinewidth=0.5, markersize=2, linewidth=0.5, fmt='.'
        )
        for cap in caps:
            cap.set_markeredgewidth(0.5)
        if coeff:
            x = np.linspace(nudge.min(), nudge.max(), 100)
            self.ax.plot(x, polyval(x, coeff), '--', alpha=0.7)

    def finish(self):
        self.ax.set_xlabel("DAC Nudge")
        self.ax.set_ylabel(self.y_label)
        self.ax.xaxis.set_major_locator(MultipleLocator(5))
        self.ax.grid(
            b=True, which='major', color='gray', linestyle='-', alpha=0.2
        )


def main():
    pm = PixelMasks()
    dead = np.where(np.logical_or(pm.dead, np.repeat(pm.bad_hv, 4)))[0]

    spe_paths = glob(join(DATA, "spe_*.h5"))
    pattern = re.compile(r"(?:.+?)/spe_(.+?).h5")

    d_list = []

    for path in spe_paths:
        nudge = int(re.search(pattern, path).group(1))

        with pd.HDFStore(path) as store:
            metadata = store.get_storer('metadata').attrs.metadata
            coeff = store['coeff_pixel']
            errors = store['errors_pixel']

        coeff = coeff.loc[~coeff['pixel'].isin(dead)]
        errors = errors.loc[~errors['pixel'].isin(dead)]
        coeff_average = coeff.mean()
        errors_average = errors.mean()
        n_illuminations = metadata['n_illuminations']

        cc = np.zeros(n_illuminations)
        lambda_ = np.zeros(n_illuminations)
        lambda_error = np.zeros(n_illuminations)
        for ill in range(n_illuminations):
            eped = coeff_average['eped']
            cc[ill] = coeff_average[f'charge_average{ill}'] - eped
            lambda_[ill] = coeff_average[f'lambda_{ill}']
            lambda_error[ill] = errors_average[f'lambda_{ill}']
        cc2pe_ped, cc2pe = polyfit(
            lambda_, cc, [1], w=1/lambda_error
        )

        p_ccvslambda = CCVsLambda()
        p_ccvslambda.plot(
            cc, lambda_, lambda_error, cc2pe_ped, cc2pe
        )
        plot_path = join(RESULTS, f"cc_vs_lambda_{nudge:+d}.pdf")
        p_ccvslambda.save(plot_path)

        d_list.append(dict(
            nudge=nudge,
            opct=coeff_average['opct'],
            opct_err=errors_average['opct'],
            spe=coeff_average['spe'],
            spe_err=errors_average['spe'],
            spe_sigma=coeff_average['spe_sigma'],
            spe_sigma_err=errors_average['spe_sigma'],
            eped=coeff_average['eped'],
            eped_err=errors_average['eped'],
            eped_sigma=coeff_average['eped_sigma'],
            eped_sigma_err=errors_average['eped_sigma'],
            cc2pe=cc2pe,
            cc2pe_ped=cc2pe_ped,
        ))

    df = pd.DataFrame(d_list)

    output_path = join(RESULTS, "spe.csv")
    df.to_csv(output_path, index=False)

    nudge = df['nudge'].values

    y = df['opct'].values
    yerr = df['opct_err'].values
    ylabel = "Optical Crosstalk"
    plot_path = join(RESULTS, f"opct.pdf")
    p_params = ParamPlotter(ylabel)
    p_params.plot(nudge, y, yerr)
    p_params.save(plot_path)

    y = df['spe'].values
    yerr = df['spe_err'].values
    ylabel = "Gain (cc mVns)"
    plot_path = join(RESULTS, f"spe.pdf")
    p_params = ParamPlotter(ylabel)
    p_params.plot(nudge, y, yerr)
    p_params.save(plot_path)

    y = df['eped'].values
    yerr = df['eped_err'].values
    ylabel = "Eped (cc mVns)"
    plot_path = join(RESULTS, f"eped.pdf")
    p_params = ParamPlotter(ylabel)
    p_params.plot(nudge, y, yerr)
    p_params.save(plot_path)

    y = df['cc2pe_ped'].values
    yerr = None
    ylabel = "cc2pe Pedestal (cc mVns)"
    plot_path = join(RESULTS, f"cc2pe_pedestal.pdf")
    p_params = ParamPlotter(ylabel)
    p_params.plot(nudge, y, yerr)
    p_params.save(plot_path)

    y = df['cc2pe'].values
    yerr = None
    ylabel = "cc2pe (cc mVns / p.e.)"
    plot_path = join(RESULTS, f"cc2pe.pdf")
    p_params = ParamPlotter(ylabel)
    p_params.plot(nudge, y, yerr)
    p_params.save(plot_path)


if __name__ == '__main__':
    main()
