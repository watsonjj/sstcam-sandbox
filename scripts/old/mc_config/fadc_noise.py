import os
import numpy as np
import pandas as pd
from CHECLabPy.plotting.setup import Plotter
from CHECLabPy.spectrum_fitters.gentile import pedestal_signal, K
from CHECLabPy.waveform_reducers.cross_correlation import CrossCorrelation
from target_calib import CameraConfiguration


class SPEHist(Plotter):
    def plot(self, hist, edges, between, x, y, label):
        self.ax.hist(between, bins=edges, weights=hist, alpha=0.2)
        self.ax.plot(x, y, label=label)

    def finish(self):
        self.ax.set_xlabel("Amplitude (mV)")
        self.ax.set_ylabel("N")
        self.add_legend()


def main():
    input_path = "/Volumes/gct-jason/data_checs/dynamicrange_180514/tf_pchip/spe_three.h5"
    file_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(file_dir, "outputs")

    dead = [677, 293, 27, 1925]

    store = pd.HDFStore(input_path)
    df = store['coeff_pixel']
    df_array = store['array_camera']
    df = df.loc[~df['pixel'].isin(dead)]
    df_mean = df.mean().to_dict()

    norm = (df_mean['norm0'] + df_mean['norm1'] + df_mean['norm2'])/3

    config = CameraConfiguration("1.1.0")
    ref_path = config.GetReferencePulsePath()
    cc = CrossCorrelation(1, 96, reference_pulse_path=ref_path)

    d = dict(
        norm=1,
        eped=cc.get_pulse_height(df_mean['eped']),
        eped_sigma=cc.get_pulse_height(df_mean['eped_sigma']),
        lambda_=1
    )

    hist = df_array.loc[0, 'hist'] / (norm * 1000)
    edges = cc.get_pulse_height(df_array.loc[0, 'edges'])
    between = cc.get_pulse_height(df_array.loc[0, 'between'])

    x = np.linspace(-5, 15, 1000)
    y = pedestal_signal(x, **d)

    p_hist = SPEHist()
    label = "fadc_noise = eped_sigma = {:.3f}".format(d['eped_sigma'])
    p_hist.plot(hist, edges, between, x, y, label)
    output_path = os.path.join(output_dir, "checs_fadc_noise.pdf")
    p_hist.save(output_path)


if __name__ == '__main__':
    main()
