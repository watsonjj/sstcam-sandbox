from spefit import BinnedNLL, ChargeContainer, SiPMModifiedPoisson, minimize_with_iminuit, UnbinnedNLL
from sstcam_sandbox.d201202_tutorial_material import poi, matched_voltage, nsb
from CHECLabPy.core.io import HDF5Reader, HDF5Writer
from sstcam_sandbox import get_data, get_plot
import numpy as np
from numpy.polynomial.polynomial import polyfit
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from tqdm import trange
from IPython import embed
from CHECLabPy.waveform_reducers.cross_correlation import CrossCorrelation
import pickle


def plot_spe(result, matched_voltage):
    n_pixels = len(result.pixel_values)
    output_path = get_plot(f"d200805_charge_resolution/5_spe_fitting/spe_0MHz_{matched_voltage}mV.pdf")
    with PdfPages(output_path) as pdf:
        for pixel in trange(n_pixels):
            fig, ax = plt.subplots()

            n_illuminations = result.n_illuminations
            for illumination in range(n_illuminations):
                hist_x = result.pixel_arrays[pixel][illumination]['charge_hist_x']
                hist_y = result.pixel_arrays[pixel][illumination]['charge_hist_y']
                hist_edges = result.pixel_arrays[pixel][illumination]['charge_hist_edges']
                fit_x = result.pixel_arrays[pixel][illumination]['fit_x']
                fit_y = result.pixel_arrays[pixel][illumination]['fit_y']
                lambda_ = result.pixel_values[pixel][f'lambda_{illumination}']
                lambda_err = result.pixel_errors[pixel][f'lambda_{illumination}']
                label = f"λ = {lambda_:.3f} ± {lambda_err:.3f} p.e."

                hist_y = hist_y / np.sum(hist_y * (hist_x[1] - hist_x[0]))

                color = plt.gca()._get_lines.get_next_color()
                ax.hist(hist_x, weights=hist_y, bins=hist_edges, histtype='step', color=color)
                ax.plot(fit_x, fit_y, label=label, color=color)

                # initial_x = result.pixel_arrays[pixel]['initial_x']
                # initial_y = result.pixel_arrays[pixel]['initial_y'][illumination]
                # d = result.pixel_arrays[pixel]['d']
                # ax.plot(initial_x, initial_y, label=f"initial lambda={d['lambda_']:.2f} eped={d['eped']:.2f} eped_sigma={d['eped_sigma']:.2f} spe={d['spe']:.2f} spe_sigma={d['spe_sigma']:.2f} opct={d['opct']:.2f}")

            # if pixel == 3:
            #     np.savez("/Users/Jason/Downloads/SiPM-pulse-height-analysis-master/test.npz", arr_0=hist_x, arr_1=hist_y)
            #     plt.show()
            #     exit()

            opct = result.pixel_values[pixel]['opct']
            opct_err = result.pixel_errors[pixel]['opct']

            ax.set_xlabel("Charge (~p.e.)")
            ax.set_ylabel("N")
            ax.set_title(f"0MHz {matched_voltage}mV, Pixel = {pixel}, OPCT = {opct:.3f} ± {opct_err:.3f}")
            ax.legend(loc='best')

            pdf.savefig(fig)
            plt.close(fig)


# def plot_spe_all_pixels(result, matched_voltage):



def main():
    initial = dict(
            eped=-1,
            eped_sigma=0.27,
            pe=2.4,
            pe_sigma=0.06,
            opct=0.25,
            lambda_0=0.63,
            lambda_1=0.84,
            lambda_2=1.07,
    )
    path = get_data(f"d200805_charge_resolution/1_extract_lab_old/charge_0MHz_{matched_voltage}mV.h5")
    with HDF5Reader(path) as reader:
        df = reader.read('data')
        df = df.loc[df['pixel'] == poi]

    spe_illuminations = np.unique(df['expected_illumination_pe'])[5:8]
    n_illuminations = len(spe_illuminations)

    charges_raw = []
    pulse_path = "/Users/Jason/Software/sstcam-simulation/tutorials/d201209_workshop/pulse_shape.txt"
    cc = CrossCorrelation(1, 1, reference_pulse_path=pulse_path)
    for illumination in spe_illuminations:
        df_i = df.loc[df['expected_illumination_pe'] == illumination]
        charge = cc.get_pulse_height(df_i['charge'].values)
        charges_raw.append(ChargeContainer(charge, n_bins=100, range_=(-3, 15)))

    pdf = SiPMModifiedPoisson(n_illuminations)
    pdf.update_parameters_initial(**initial)
    cost = UnbinnedNLL(pdf, charges_raw)
    values, errors = minimize_with_iminuit(cost)

    charges = []
    for container in charges_raw:
        charge = container.values - values['eped']
        charges.append(ChargeContainer(charge, n_bins=100, range_=(-3, 15)))

    pdf = SiPMModifiedPoisson(n_illuminations)
    pdf.update_parameters_initial(**initial)
    cost = UnbinnedNLL(pdf, charges)
    values, errors = minimize_with_iminuit(cost)
    values_array = np.array(list(values.values()))

    output = dict(
        n_illuminations=n_illuminations,
        hist=[],
        between=[],
        edges=[],
        fit_x=[],
        fit_y=[],
        values=values,
        errors=errors
    )

    fig = plt.figure(figsize=(10, 5))
    for i in range(n_illuminations):
        ax = fig.add_subplot(n_illuminations, 1, i+1)
        ax.hist(
            charges[i].between,
            weights=charges[i].hist,
            bins=charges[i].edges,
            density=True,
            histtype='step',
        )

        fit_x = np.linspace(charges[i].edges.min(), charges[i].edges.max(), 1000)
        fit_y = pdf(fit_x, values_array, i)
        lambda_ = values[f'lambda_{i}']
        lambda_err = errors[f'lambda_{i}']
        label = f"λ = {lambda_:.3f} ± {lambda_err:.3f} p.e."
        ax.plot(fit_x, fit_y, label=label)
        ax.legend()

        output['hist'].append(charges[i].hist)
        output['between'].append(charges[i].between)
        output['edges'].append(charges[i].edges)
        output['fit_x'].append(fit_x)
        output['fit_y'].append(fit_y)
    output_path = get_plot(f"d201202_tutorial_material/spe_0MHz_{matched_voltage}mV.pdf")
    fig.savefig(output_path)

    output_path = get_data(f"d201202_tutorial_material/spe_0MHz_{matched_voltage}mV.pkl")
    with open(output_path, 'wb') as file:
        pickle.dump(output, file, protocol=pickle.HIGHEST_PROTOCOL)


if __name__ == '__main__':
    main()
