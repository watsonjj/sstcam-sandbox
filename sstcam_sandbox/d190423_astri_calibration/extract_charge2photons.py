from os.path import join
import numpy as np
import pandas as pd
import yaml
from sstcam_sandbox import get_astri_2019
from CHECLabPy.calib import PixelMasks, SiPMDataSheetConverter
from CHECLabPy.core.io import HDF5Reader
from CHECLabPy.plotting.setup import Plotter
from CHECOnsky.calib import get_calib_data
from matplotlib.ticker import MultipleLocator
from numpy.polynomial.polynomial import polyfit, polyval
from IPython import embed


class Mv2pePlotter(Plotter):
    def plot(self, nudge, mv2pe, coeff, xmin, xmax):
        self.ax.plot(nudge, mv2pe, 'x')
        x = np.linspace(xmin, xmax, 100)
        self.ax.plot(x, polyval(x, coeff), '--', alpha=0.7)

        self.ax.set_xlabel("DAC Nudge")
        self.ax.set_ylabel("mV per photoelectron")
        self.ax.xaxis.set_major_locator(MultipleLocator(5))
        self.ax.grid(
            b=True, which='major', color='gray', linestyle='-', alpha=0.2
        )


class PDEPlotter(Plotter):
    def plot(self, nudge, pde, coeff=None):
        self.ax.plot(nudge, pde, 'x')
        if coeff:
            x = np.linspace(nudge.min(), nudge.max(), 100)
            self.ax.plot(x, polyval(x, coeff), '--', alpha=0.7)

    def finish(self):
        self.ax.set_xlabel("DAC Nudge")
        self.ax.set_ylabel("Photon Detection Efficiency")
        self.ax.xaxis.set_major_locator(MultipleLocator(5))
        self.ax.grid(
            b=True, which='major', color='gray', linestyle='-', alpha=0.2
        )


def calculate_illumination(df_bright, df_spe):
    df_nominal_bright = df_bright.loc[df_bright['nudge'] == 0].mean()
    nominal_bright_cc = df_nominal_bright['cc']

    nominal_spe = df_spe[df_spe['nudge'] == 0]
    nominal_cc2pe = nominal_spe['cc2pe'][0]
    nominal_opct = nominal_spe['opct'][0]

    converter = SiPMDataSheetConverter()
    pde = converter(opct=nominal_opct)['pde']

    pe = nominal_bright_cc / nominal_cc2pe
    photons = pe / pde

    print(f"Nominal Illumination: {photons:.2f} photons "
          f"({pe:.2f} p.e. @ PDE={pde:.2f})")

    return photons


def calculate_cc2height(df_bright):
    df_nominal_bright = df_bright.loc[df_bright['nudge'] == 0].mean()
    nominal_charge = df_nominal_bright['cc']
    nominal_height = df_nominal_bright['waveform_max']
    return nominal_charge / nominal_height


def main():
    pm = PixelMasks()
    dead = np.where(np.logical_or(pm.dead, np.repeat(pm.bad_hv, 4)))[0]

    bright_path = get_astri_2019("d2019-04-23_nudges/bright_50pe/charge.h5")
    with HDF5Reader(bright_path) as reader:
        df_bright = reader.read("data").groupby(
            ['nudge', 'pixel']
        ).mean().reset_index()
        isin_dead = df_bright['pixel'].isin(dead)
        df_bright = df_bright.loc[~isin_dead]

    spe_path = get_astri_2019("d2019-04-23_nudges/results/process_spe/spe.csv")
    df_spe = pd.read_csv(spe_path)

    illumination = calculate_illumination(df_bright, df_spe)
    cc2height = calculate_cc2height(df_bright)
    print(f"charge2height = {cc2height}")

    nudges = np.unique(df_bright['nudge'])
    # nudges = np.delete(nudges, np.where(np.isin(nudges, [5, 25])))
    mv2pe = np.zeros(nudges.size)
    charge2photons = np.zeros(nudges.size)
    pde = np.zeros(nudges.size)

    for inudge, nudge in enumerate(nudges):
        df_bright_nudge = df_bright.loc[df_bright['nudge'] == nudge].mean()
        df_spe_nudge = df_spe.loc[df_spe['nudge'] == nudge]

        cc2pe = df_spe_nudge['cc2pe'].iloc[0]
        mv2pe[inudge] = cc2pe / cc2height

        charge_onsky = df_bright_nudge['onsky_calib']
        charge2photons[inudge] = charge_onsky / illumination

        charge_cc = df_bright_nudge['cc']
        cc2photons = charge_cc / illumination
        pde[inudge] = cc2photons / cc2pe

    mask = ~np.isin(nudges, [5, 25])
    mv2pe_coeff = polyfit(nudges[mask], mv2pe[mask], 3)
    charge2photons_coeff = polyfit(nudges, charge2photons, 3)
    min_ = nudges.min()
    max_ = nudges.max()

    output_dir = get_astri_2019(
        "d2019-04-23_nudges/results/extract_charge2photons"
    )

    p_mv2pe = Mv2pePlotter()
    p_mv2pe.plot(nudges[mask], mv2pe[mask], mv2pe_coeff, min_, max_)
    p_mv2pe.save(join(output_dir, "mv2pe.pdf"))

    p_mv2pe_cc = Mv2pePlotter()
    p_mv2pe_cc.plot(nudges, charge2photons, charge2photons_coeff, min_, max_)
    p_mv2pe_cc.ax.set_ylabel("Charge (mVns) per photon")
    p_mv2pe_cc.save(join(output_dir, "charge2photons.pdf"))

    p_pde = PDEPlotter()
    p_pde.plot(nudges[mask], pde[mask])
    p_pde.save(join(output_dir, "pde.pdf"))

    output = dict(
        charge2photons_coeff=charge2photons_coeff.tolist(),
        nudge_min=-40, #int(nudges.min()),
        nudge_max=int(nudges.max()),
    )
    outpath = get_calib_data('charge2photons.yml')
    with open(outpath, 'w') as outfile:
        yaml.dump(output, outfile, default_flow_style=False)
    print(f"Created charge2photons file: {outpath}")


if __name__ == '__main__':
    main()
