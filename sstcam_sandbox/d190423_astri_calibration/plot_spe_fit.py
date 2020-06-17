from sstcam_sandbox import get_astri_2019
from os.path import join, abspath, dirname
import numpy as np
import pandas as pd
from CHECLabPy.calib import PixelMasks
from CHECLabPy.plotting.setup import Plotter
from CHECLabPy.core.io import DL1Reader
from CHECLabPy.spectrum_fitters.gentile import SiPMGentileFitter

DIR = abspath(dirname(__file__))
DATA = get_astri_2019("d2019-04-23_nudges")


class SPEPlotter(Plotter):
    def plot(self, fitter):
        color = next(self.ax._get_lines.prop_cycler)['color']

        hist_x, hist_y, hist_edges = fitter.charge_histogram
        fit_x, fit_y = fitter.fit_result_curve
        values = fitter.fit_result_values
        errors = fitter.fit_result_errors
        n_illuminations = fitter.n_illuminations

        for i in range(n_illuminations):
            lambda_ = values['lambda_{}'.format(i)]
            lambda_err = errors['lambda_{}'.format(i)]

            self.ax.hist(
                hist_x, weights=hist_y[i], bins=hist_edges, histtype='step', color=color
            )
            self.ax.plot(
                fit_x, fit_y[i], color=color, label=f"{lambda_:.3f} ± {lambda_err:.3f} p.e."
            )

        self.add_legend()
        self.ax.set_xlabel("Charge (mV ns)")
        self.ax.set_ylabel("N")


def process(spe_paths, spe_config, output_path, poi):
    readers = [DL1Reader(path) for path in spe_paths]
    n_illuminations = len(readers)
    fitter = SiPMGentileFitter(n_illuminations, spe_config)

    charges = []
    for reader in readers:
        pixel, charge = reader.select_columns(['pixel', 'charge_cc'])
        charge_p = charge[pixel == poi]
        charges.append(charge_p)
    fitter.apply(*charges)

    p_spe = SPEPlotter()
    p_spe.plot(fitter)
    p_spe.save(output_path)


def main():
    pm = PixelMasks()
    dead = np.where(np.logical_or(pm.dead, np.repeat(pm.bad_hv, 4)))[0]

    poi = 811
    assert poi not in dead

    spe_config = join(DIR, "spe_config.yml")
    df_spe = pd.read_csv(join(DIR, "spe_runlist.txt"), sep='\t')
    for _, row in df_spe.iterrows():
        nudge = row['nudge']
        spe_paths = [
            join(DATA, f"spe_0.5pe/{row['spe_0.5pe']}"),
            join(DATA, f"spe_0.8pe/{row['spe_0.8pe']}"),
            join(DATA, f"spe_1.1pe/{row['spe_1.1pe']}"),
            join(DATA, f"spe_1.7pe/{row['spe_1.7pe']}"),
            join(DATA, f"spe_2.4pe/{row['spe_2.4pe']}"),
        ]
        output_path = join(DATA, f"spe_{nudge:+d}.pdf")
        process(spe_paths, spe_config, output_path, poi)


if __name__ == '__main__':
    main()
