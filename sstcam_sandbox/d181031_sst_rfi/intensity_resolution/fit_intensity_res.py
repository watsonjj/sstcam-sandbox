from sstcam_sandbox.plotting.setup import Plotter
from sstcam_sandbox.old.io import HDF5Reader, HDF5Writer
from sstcam_sandbox.d181031_sst_rfi.intensity_resolution import fit_files
# from sstcam_sandbox.utils.sipm import PE2Photons
# from ThesisAnalysis.files import Lab_TFPoly, MCLab_Opct40_5MHz, CHECM
# from ThesisAnalysis.plotting.resolutions import ChargeResolutionWRRPlotter
import numpy as np
import pandas as pd
import iminuit
from scipy.stats import poisson


def sigma_0(nsb, window_size, electronic_noise):
    # Convert from MHz to pe/ns
    nsb /= 1000
    return np.sqrt(nsb * window_size + electronic_noise ** 2)


class Fitter:
    def __init__(self):
        self.p0 = dict(
            sigma_0=sigma_0(0.125, 15, 0.87),
            enf=1.25,
            miscal=0.1,
            # pde=0.25
        )
        self.limits = dict(
            limit_sigma_0=(0, 10),
            limit_enf=(1.12, 1.5),
            limit_miscal=(0, 0.5),
            # limit_pde=(0.05, 0.7)
        )
        self.fix = dict(
        )

    @staticmethod
    def intensity_resolution(n, sigma_0=sigma_0(0.125, 15, 0.87), enf=1.2, miscal=0.1, pde=0.25):
        # pe2photons = PE2Photons()
        q = n * pde
        res = np.sqrt(sigma_0 ** 2 + enf ** 2 * q +(miscal * q) ** 2) / q
        # embed()
        return res

    def fit(self, x, y):
        yreq = self.intensity_resolution(x)

        def minimize(sigma_0, enf, miscal):
            # pe2photons = PE2Photons()
            pde = 0.25#1 / pe2photons.convert(enf - 1)
            p = self.intensity_resolution(
                x, sigma_0, enf, miscal, pde
            )
            like = -2 * poisson._logpmf(y / yreq, p / yreq)
            sum_ = np.sum(like ** 2)
            return sum_

        m0 = iminuit.Minuit(minimize, **self.p0, **self.limits, **self.fix,
                            print_level=0, pedantic=False, throw_nan=True)
        m0.migrad()
        coeff = m0.values
        m0.hesse()
        errors = m0.errors

        return coeff, errors


class FitPlotter(Plotter):

    def plot(self, x, y, xf, yf, yopct_geo, yopct_branching):
        req_x = Fitter.intensity_resolution(x)
        req_xf = Fitter.intensity_resolution(xf)

        y /= req_x
        yf /= req_xf
        yopct_geo /= req_xf
        yopct_branching /= req_xf

        self.ax.plot(x, y, ',')

        self.ax.plot(xf, yf)
        self.ax.plot(xf, yopct_geo, label='geo')
        self.ax.plot(xf, yopct_branching, label='branching')

        self.ax.set_xscale('log')

        self.add_legend("best")

    def add_text(self, coeff, errors):
        text = ""
        for c in coeff.keys():
            text += c
            text += " = {:#.3g} ± {:#.3g}\n".format(coeff[c], errors[c])
        self.ax.text(0.01, 0.99, text, va='top', ha='left', transform=self.ax.transAxes, fontsize=6)


def process(file):
    path = file.intensity_resolution_path
    dead = file.dead
    output_path = file.fit_intensity_res_path
    plot_path = file.fit_intensity_res_plot_path

    with HDF5Reader(path) as reader:
        df = reader.read('charge_resolution_pixel')
        df = df.loc[df['true'] < 200]
        df = df.loc[~df['pixel'].isin(dead)]

    fitter = Fitter()

    x = df['true'].values
    y = df['charge_resolution'].values

    # embed()
    coeff, errors = fitter.fit(x, y)

    for c in coeff.keys():
        print(c, "{:#.3g} ± {:#.3g}".format(coeff[c], errors[c]))

    opct_geo = coeff['enf'] - 1
    roots = np.roots([3/2, 1, -1 * (coeff['enf'] - 1)])
    opct_branching = roots[roots>0][0]

    print("opct (geo)", opct_geo)
    print("opct (branching)", opct_branching)
    # pe2photons = PE2Photons()
    # embed()
    # print("pde (from curve)", 1/pe2photons.convert(opct_geo))

    xf = np.geomspace(0.1, 4000, 100)
    yf = fitter.intensity_resolution(xf, **coeff)

    # coeff['sigma_0'] = sigma_0(125, 15, 0.3)
    ynsb = fitter.intensity_resolution(xf, **coeff)

    coeff_geo = dict(coeff)
    coeff_geo['pde'] = 0.39
    opct = 0.08
    coeff_geo['enf'] = 1 + opct
    yopct_geo = fitter.intensity_resolution(xf, **coeff_geo)

    coeff_branching = dict(coeff)
    coeff_branching['pde'] = 0.39
    coeff_branching['enf'] = 1 + opct + (3/2) * opct ** 2
    yopct_branching = fitter.intensity_resolution(xf, **coeff_branching)

    df = pd.DataFrame(dict(
        x=xf,
        y=yf,
        yopct=yopct_geo,
    ))

    with HDF5Writer(output_path) as writer:
        writer.write(data=df)

    p_fit = FitPlotter()
    p_fit.plot(x, y, xf, yf, yopct_geo, yopct_branching)
    p_fit.add_text(coeff, errors)
    p_fit.save(plot_path)


def main():
    [process(f) for f in fit_files]

if __name__ == '__main__':
    main()
