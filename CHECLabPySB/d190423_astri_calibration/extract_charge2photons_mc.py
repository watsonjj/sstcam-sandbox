import numpy as np
from CHECLabPySB import get_astri_2019
from CHECOnsky.calib import get_calib_data
from CHECLabPy.calib import PixelMasks
from CHECLabPy.core.io import HDF5Reader
from CHECLabPy.plotting.setup import Plotter
from numpy.polynomial.polynomial import polyfit, polyval
from os.path import join
import yaml


class CalibPlotter(Plotter):
    def plot(self, true, measured, coeff):
        self.ax.plot(true, measured, '.')

        x = np.linspace(true.min(), true.max(), 100)
        y = polyval(x, coeff)
        self.ax.plot(x, y)

        self.ax.set_xlabel("True Charge (photons)")
        self.ax.set_ylabel("Measured Charge")


def main():
    pixel_mask_path = get_astri_2019(
        "d2019-04-23_nudges/mc/mc_chec_pixel_mask_190521.dat"
    )
    pm = PixelMasks(pixel_mask_path)
    dead = np.where(pm.all_mask)[0]

    path = get_astri_2019("d2019-04-23_nudges/mc/charge.h5")
    output_path = get_calib_data("charge2photons_simtel.yml")
    pde = 0.25

    with HDF5Reader(path) as reader:
        df = reader.read("data")
        df = df.loc[df['mc_true'] > 5]
        isin_dead = df['pixel'].isin(dead)
        df = df.loc[~isin_dead]

    measured = df['onsky'].values
    true = df['mc_true'].values / pde

    coeff = polyfit(true, measured, [1])
    _, charge2photons = coeff

    print(f"charge2photons = {charge2photons}")

    results_dir = get_astri_2019(
        "d2019-04-23_nudges/results/extract_charge2photons_mc"
    )

    p_calib = CalibPlotter()
    p_calib.plot(true, measured, coeff)
    p_calib.save(join(results_dir, "calib.pdf"))

    output = dict(
        charge2photons=float(charge2photons),
    )
    with open(output_path, 'w') as outfile:
        yaml.dump(output, outfile, default_flow_style=False)
    print(f"Created charge2photons file: {output_path}")


if __name__ == '__main__':
    main()
