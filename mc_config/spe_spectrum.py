"""
Executable for plotting the extractd fit parameters from extract_spe
"""
import argparse
import os
from argparse import ArgumentDefaultsHelpFormatter as Formatter
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import warnings
from CHECLabPy.plotting.setup import Plotter
from CHECLabPy.plotting.spe import SpectrumFitPlotter
from CHECLabPy.plotting.camera import CameraImage
from CHECLabPy.spectrum_fitters.gentile import pe_signal, K
from IPython import embed


class SPECamera:
    def __init__(self, mapping, output_dir):
        self.camera = CameraImage.from_mapping(mapping)
        self.camera.add_colorbar()
        self.output_dir = output_dir

    def produce(self, df):
        pixel = df['pixel'].values
        columns = df.columns
        d = self.output_dir
        for c in columns:
            if c == 'pixel':
                continue
            image = df[c].values[pixel]
            self.camera.image = image
            self.camera.ax.set_title(c)
            output_path = os.path.join(d, "camera_{}.pdf".format(c))
            self.camera.save(output_path)


class SPEHist(Plotter):
    def __init__(self, output_dir):
        super().__init__()
        self.output_dir = output_dir

    def produce(self, df):
        pixel = df['pixel'].values
        columns = df.columns
        d = self.output_dir
        for c in columns:
            self.fig, self.ax = self.create_figure()
            if c == 'pixel':
                continue
            values = df[c].values[pixel]
            mean = np.mean(values)
            std = np.std(values)
            label = "Mean = {:.3g}, Stddev = {:.3g}".format(mean, std)
            self.ax.hist(values, bins='scott', label=label)
            self.add_legend()
            self.ax.set_title(c)
            output_path = os.path.join(d, "hist_{}.pdf".format(c))
            self.save(output_path)


def main():
    description = 'Plot the contents of the spe HDF5 file'
    parser = argparse.ArgumentParser(description=description,
                                     formatter_class=Formatter)
    parser.add_argument('-f', '--file', dest='input_path', action='store',
                        required=True,
                        help='path to the input spe HDF5 file')
    parser.add_argument('-o', '--output', dest='output_path', action='store',
                        required=True,
                        help='path to store the output spectrum')
    args = parser.parse_args()

    input_path = args.input_path
    output_path = args.output_path

    dead = [677, 293, 27, 1925]

    store = pd.HDFStore(input_path)
    df = store['coeff_pixel']
    df = df.loc[~df['pixel'].isin(dead)]
    d = df.mean().to_dict()
    keys = list(d.keys())

    for key in keys:
        if key in ['pixel', 'chi2', 'rchi2', 'p_value']:
            d.pop(key)
        if key.startswith('lambda'):
            d.pop(key)
        if key.startswith('norm'):
            d.pop(key)
    d['norm'] = 1
    d['lambda_'] = 1
    d['eped'] = 0
    d['eped_sigma'] = 0
    spe = d['spe']
    d['spe'] /= spe
    d['spe_sigma'] /= spe

    x = np.linspace(0, 20, 1000)
    y = pe_signal(K, x[None, :], **d).sum(0)

    plt.plot(x, y)

    plt.show()

    embed()

    # p_camera = SPECamera(mapping, output_dir)
    # p_camera.produce(df_pixel_coeff)
    # plt.close("all")
    #
    # p_hist = SPEHist(output_dir)
    # p_hist.produce(df_pixel_coeff)
    # plt.close("all")
    #
    # p_spectrum_pixel = SpectrumFitPlotter()
    # p_spectrum_pixel.plot_from_df_pixel(df_pixel_coeff, df_pixel_initial,
    #                                     df_pixel_array, metadata, plot_pixel)
    # p_spectrum_pixel.save(os.path.join(output_dir, "spectrum_pixel.pdf"))
    #
    # p_spectrum_camera = SpectrumFitPlotter()
    # p_spectrum_camera.plot_from_df_camera(df_camera_coeff, df_camera_initial,
    #                                       df_camera_array, metadata)
    # p_spectrum_camera.save(os.path.join(output_dir, "spectrum_camera.pdf"))


if __name__ == '__main__':
    main()
