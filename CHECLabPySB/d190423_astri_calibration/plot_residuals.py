from CHECLabPySB import get_astri_2019
from CHECLabPySB.d190423_astri_calibration.extract_charge2photons import \
    calculate_illumination
import numpy as np
import pandas as pd
from CHECLabPy.core.io import HDF5Reader
from CHECLabPy.calib import PixelMasks
from CHECLabPy.plotting.setup import Plotter
from matplotlib.ticker import MultipleLocator
from os.path import join
from CHECOnsky.calib import OnskyAmplitudeCalibrator


class CalibratedvsNudge(Plotter):
    def __init__(self, xlabel, ylabel):
        super().__init__()
        self.xlabel = xlabel
        self.ylabel = ylabel

    def plot(self, nudge, mean, std):
        (_, caps, _) = self.ax.errorbar(
            nudge, mean, yerr=std, mew=1, capsize=1, elinewidth=0.5,
            markersize=2, linewidth=0.5, fmt='.'
        )
        for cap in caps:
            cap.set_markeredgewidth(0.5)

    def finish(self):
        self.ax.set_xlabel(self.xlabel)
        self.ax.set_ylabel(self.ylabel)
        self.ax.xaxis.set_major_locator(MultipleLocator(5))
        self.ax.grid(
            b=True, which='major', color='gray', linestyle='-', alpha=0.1
        )


def main():
    pm = PixelMasks()
    dead = np.where(np.logical_or(pm.dead, np.repeat(pm.bad_hv, 4)))[0]

    bright_path = get_astri_2019("d2019-04-23_nudges/bright_50pe/charge.h5")
    with HDF5Reader(bright_path) as reader:
        df_bright = reader.read("data")
        isin_dead = df_bright['pixel'].isin(dead)
        df_bright = df_bright.loc[~isin_dead]

    spe_path = get_astri_2019("d2019-04-23_nudges/results/process_spe/spe.csv")
    df_spe = pd.read_csv(spe_path)

    illumination = calculate_illumination(df_bright, df_spe)

    d_list = []

    for nudge, group in df_bright.groupby("nudge"):
        temperatures = group['temperature'].values
        assert (temperatures == temperatures[0]).all()
        temperature = temperatures[0]

        calibrator = OnskyAmplitudeCalibrator(nudge, temperature)

        pixel = group['pixel'].values
        charge = group['onsky_calib'].values
        charge_cal = calibrator(charge, pixel)

        group_avg = group.groupby('pixel').mean()
        pixel_avg = group_avg.index.values
        charge_avg = group_avg['onsky_calib'].values
        charge_avg_cal = calibrator(charge_avg, pixel_avg)

        rmse = np.sqrt(
            np.sum((illumination - charge_cal) ** 2) / charge_cal.size
        )

        d_list.append(dict(
            nudge=nudge,
            mean=charge_cal.mean(),
            std=charge_cal.std(),
            mean_avg=charge_avg_cal.mean(),
            std_avg=charge_avg_cal.std(),
            rmse=rmse,
        ))

    df = pd.DataFrame(d_list)

    output_dir = get_astri_2019("d2019-04-23_nudges/results/plot_residuals")

    p_cal = CalibratedvsNudge("DAC Nudge", "Calibrated Charge (photons)")
    p_cal.plot(df['nudge'], df['mean'], df['std'])
    p_cal.ax.axhline(illumination, color='red', alpha=0.2, lw=0.2)
    p_cal.save(join(output_dir, "calibrated_vs_nudge.pdf"))

    p_avg = CalibratedvsNudge("DAC Nudge", "Average Charge (photons)")
    p_avg.plot(df['nudge'], df['mean_avg'], df['std_avg'])
    p_avg.ax.axhline(illumination, color='red', alpha=0.2, lw=0.2)
    p_avg.save(join(output_dir, "calibrated_vs_nudge_avg.pdf"))

    p_rmse = CalibratedvsNudge("DAC Nudge", f"RMSE {illumination:.2f} photons")
    p_rmse.plot(df['nudge'], df['rmse'], None)
    p_rmse.save(join(output_dir, "rmse_vs_nudge.pdf"))


if __name__ == '__main__':
    main()
