from CHECLabPy.spectrum_fitters.gentile import SiPMGentileFitter, SpectrumParameter, sipm_gentile_spe
import numpy as np
import pandas as pd
from multiprocessing import Pool, Manager, cpu_count
from tqdm import trange
import re
from matplotlib import pyplot as plt
from IPython import embed


class FitApplier:
    def __init__(self, fitter):
        self.fitter = fitter

        manager = Manager()
        self.pixel_values = manager.dict()
        self.pixel_errors = manager.dict()
        self.pixel_arrays = manager.dict()

        self.charges = None

    def _apply_pixel(self, pixel):
        n_illuminations = self.fitter.n_illuminations
        pixel_charges = [self.charges[i][:, pixel] for i in range(n_illuminations)]
        self.fitter.apply(*pixel_charges)

        charge_hist_x, charge_hist_y, charge_hist_edges = self.fitter.charge_histogram
        fit_x, fit_y = self.fitter.fit_result_curve

        self.pixel_values[pixel] = dict(self.fitter.fit_result_values)
        self.pixel_errors[pixel] = dict(self.fitter.fit_result_errors)
        self.pixel_arrays[pixel] = dict(
            charge_hist_x=charge_hist_x,
            charge_hist_y=charge_hist_y,
            charge_hist_edges=charge_hist_edges,
            fit_x=fit_x,
            fit_y=fit_y,
        )

    def multiprocess(self, charges):
        self.charges = charges
        _, n_pixels = charges[0].shape
        n_processes = int(cpu_count() * 0.75)
        print(f"Multiprocessing pixel SPE fit (n_processes = {n_processes})")
        with Pool(n_processes) as pool:
            pool.map(self._apply_pixel, trange(n_pixels))

    def process(self, charges):
        self.charges = charges
        _, n_pixels = charges[0].shape
        for pixel in trange(n_pixels):
            self._apply_pixel(pixel)


def main():
    # Define SPE
    params = dict(
        eped=-0.5,
        eped_sigma=5.7,
        spe=16,
        spe_sigma=1,
        opct=0.3,
    )
    lambda_values = [0.5, 0.7, 0.9]

    # Define run
    n_events = 30000
    n_pixels = 2#048

    # Get charges
    pdf_x = np.linspace(-40, 200, 30000, dtype=np.float32)
    pdf_y = []
    charges = []
    for lambda_ in lambda_values:
        pdf = sipm_gentile_spe(pdf_x, lambda_=lambda_, **params)
        pdf /= pdf.sum()
        charge = np.random.choice(pdf_x, (n_events, n_pixels), p=pdf)
        pdf_y.append(pdf)
        charges.append(charge)

    # Create Fitter class
    n_illuminations = len(lambda_values)
    fitter = SiPMGentileFitter(n_illuminations=n_illuminations)
    fitapplier = FitApplier(fitter)

    # Update Fit Parameters
    # spectrum_parameter_list = [
    #     SpectrumParameter("eped", 0, (-10, 10)),
    #     SpectrumParameter("eped_sigma", 1, (0.1, 2)),
    #     SpectrumParameter("spe", 3, (0.5, 5)),
    #     SpectrumParameter("spe_sigma", 2, (0.1, 2)),
    #     SpectrumParameter("opct", 0.4, (0.01, 0.8)),
    #     SpectrumParameter("lambda_", 0.7, (0.2, 5), multi=True),
    # ]
    # fitter.parameters.update(spectrum_parameter_list)
    fitter.range = (-40, 100)
    fitter.n_bins = 200

    # Perform fit
    fitapplier.process(charges)
    # fitapplier.multiprocess(charges)

    # Print parameters
    df_values = pd.DataFrame(list(fitapplier.pixel_values.values()))
    df_mean = df_values.mean()
    df_std = df_values.std()
    columns = df_values.columns
    for column in columns:
        if "lambda" in column:
            i = int(re.search(r'lambda_(\d)', column).group(1))
            true = lambda_values[i]
        elif "norm" in column:
            continue
        else:
            true = params[column]
        print(f"{column}: {df_mean[column]:.2f} ± {df_std[column]:.2f} ({true:.2f})")

    # Print parameters
    print("Pixel:")
    df_values = pd.DataFrame(list(fitapplier.pixel_values.values())).iloc[0]
    df_errors = pd.DataFrame(list(fitapplier.pixel_errors.values())).iloc[0]
    for column in columns:
        if "lambda" in column:
            i = int(re.search(r'lambda_(\d)', column).group(1))
            true = lambda_values[i]
        elif "norm" in column:
            true = 1
        else:
            true = params[column]
        print(f"{column}: {df_values[column]:.6f} ± {df_errors[column]:.6f} ({true:.2f})")

    # Plot fit for a single channel
    poi = 0
    fig = plt.figure(figsize=(5*n_illuminations, 3))
    for i in range(n_illuminations):
        ax = fig.add_subplot(1, n_illuminations, i+1)
        charge_hist_x = fitapplier.pixel_arrays[poi]['charge_hist_x']
        charge_hist_y = fitapplier.pixel_arrays[poi]['charge_hist_y'][i]
        charge_hist_edges = fitapplier.pixel_arrays[poi]['charge_hist_edges']
        fit_x = fitapplier.pixel_arrays[poi]['fit_x']
        fit_y = fitapplier.pixel_arrays[poi]['fit_y'][i]
        pdf_x = fit_x
        pdf_y = sipm_gentile_spe(pdf_x, lambda_=lambda_values[i], **params)
        pdf_norm = np.trapz(charge_hist_y, charge_hist_x) / np.trapz(pdf_y, pdf_x)
        # fit_norm = np.trapz(charge_hist_y, charge_hist_x) / np.trapz(fit_y, fit_x)
        ax.plot(pdf_x, pdf_y * pdf_norm, label="PDF")
        ax.hist(charge_hist_x, weights=charge_hist_y, bins=charge_hist_edges)
        ax.plot(fit_x, fit_y, label="Fit")
        ax.legend()
    plt.show()


if __name__ == '__main__':
    main()
