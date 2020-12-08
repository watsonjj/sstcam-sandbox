from sstcam_sandbox import get_data, get_plot
from sstcam_sandbox.d201202_tutorial_material import poi, matched_voltage, nsb
from CHECLabPy.core.io import HDF5Reader
from CHECLabPy.utils.resolutions import ChargeResolution
from CHECLabPy.plotting.resolutions import ChargeResolutionPlotter
import numpy as np
import pandas as pd
from numpy.polynomial.polynomial import polyfit, polyval
from matplotlib import pyplot as plt
from IPython import embed


def obtain_calibrated_df(path_dynrange, path_spe):
    with HDF5Reader(path_dynrange) as reader:
        df_dynrange = reader.read("data")

    with HDF5Reader(path_spe) as reader:
        df_spe_values = reader.read("values")
        df_spe_errors = reader.read("errors")
        spe_scale = reader.get_metadata()["spe_scale"]
        expected_illuminations = reader.get_metadata()["illuminations"]
        n_illuminations = len(expected_illuminations)

    def apply_calibration(df):
        ipix = int(df.iloc[0]['pixel'])
        df_spe_values_poi = df_spe_values.loc[ipix]

        # Calibrate Illumination
        measured_illuminations = np.array([df_spe_values_poi[f'lambda_{i}'] for i in range(n_illuminations)])
        c_ill = polyfit(expected_illuminations, measured_illuminations, 1)
        df['true_illumination_pe'] = polyval(df['expected_illumination_pe'], c_ill)

        # Calibration Charge
        # scale = df_spe_values_poi['pe'] * spe_scale / (1 - df_spe_values_poi['opct'])
        # df['charge_pe'] = df['charge'] / scale
        pedestal = 0#df_spe_values_poi['eped']
        df_bright = df.loc[(df['true_illumination_pe'] >= 40) & (df['true_illumination_pe'] <= 100)]
        c_charge = polyfit(df_bright['charge'] - pedestal, df_bright['true_illumination_pe'], [1])
        df['charge_pe'] = polyval(df['charge'] - pedestal, c_charge)

        return df

    return df_dynrange.groupby('pixel').apply(apply_calibration)


def obtain_charge_resolution(df_dynrange):
    measured = df_dynrange['charge_pe']
    true = df_dynrange['true_illumination_pe']
    pixel = df_dynrange['pixel']
    diff2 = np.power(measured - true, 2)
    df_cr = pd.DataFrame(dict(
        pixel=pixel,
        true=true,
        sum=diff2,
        n=np.uint32(1)
    ))
    df_cr = df_cr.groupby(['pixel', 'true']).sum().reset_index()
    df_cr['charge_res'] = np.sqrt(df_cr['sum'] / df_cr['n']) / np.abs(df_cr['true'])
    return df_cr


def plot_dynamic_range(df, nsb, matched_voltage):
    fig, ax = plt.subplots()

    df_gb = df.groupby('expected_illumination_pe').agg(['mean', 'std', 'count'])
    yerr = df_gb['charge_pe']['std']/np.sqrt(df_gb['charge_pe']['count'])
    ax.errorbar(df_gb.index, df_gb['charge_pe']['mean'], fmt='.', yerr=yerr, label="Average")
    # ax.plot(df_gb.index, df_gb['charge_pe']['mean'], ',', label="Average")

    # df_c = df.loc[(df['true_illumination_pe'] < 100) & (df['true_illumination_pe'] > 10)]
    # c = polyfit(df_c['true_illumination_pe'], df_c['charge_pe'], [1])
    # ax.plot(df_gb.index, polyval(df_gb.index, c), label="Fit")
    min_ = df['true_illumination_pe'].min()
    max_ = df['true_illumination_pe'].max()
    ax.plot([min_, max_], [min_, max_], label="1-to-1")

    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlabel("True Illumination (p.e.)")
    ax.set_ylabel("Measured Charge (p.e.)")
    ax.set_title(f"{nsb}MHz {matched_voltage}mV")
    ax.legend(loc='best')

    output_path = get_plot(f"d201202_tutorial_material/charge_{nsb}MHz_{matched_voltage}mV.pdf")
    fig.savefig(output_path)


def plot_charge_resolution(df_cr, poi, nsb, matched_voltage):
    df = df_cr.loc[df_cr['pixel'] == poi]

    x = df['true']
    y = df['charge_res']
    yerr = (1/np.sqrt(df['n'])) / x

    cr = ChargeResolutionPlotter()
    cr._plot(x, y, yerr, label="CR")
    cr.plot_poisson(x)
    cr.plot_requirement(x)

    output_path = get_plot(f"d201202_tutorial_material/cr_{nsb}MHz_{matched_voltage}mV.pdf")
    cr.save(output_path)


def main():


    path_dynrange = get_data(f"d200805_charge_resolution/1_extract_lab_old/charge_{nsb}MHz_{matched_voltage}mV.h5")
    path_spe = get_data(f"d200805_charge_resolution/5_spe_fitting/spe_0MHz_{matched_voltage}mV.h5")

    df = obtain_calibrated_df(path_dynrange, path_spe)

    plot_dynamic_range(df, nsb, matched_voltage)

    df_cr = obtain_charge_resolution(df)

    plot_charge_resolution(df_cr, poi, nsb, matched_voltage)

    output_path = get_data(f"d201202_tutorial_material/cr_{nsb}MHz_{matched_voltage}mV.txt")
    df = df_cr.loc[df_cr['pixel'] == poi]
    df.to_csv(output_path)

    # embed()


if __name__ == '__main__':
    main()
