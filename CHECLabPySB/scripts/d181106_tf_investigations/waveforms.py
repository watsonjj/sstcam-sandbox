from CHECLabPySB import get_plot
from CHECLabPySB.plotting.setup import Plotter
from CHECLabPySB.scripts.d181106_tf_investigations import *
from CHECLabPy.core.io import TIOReader, DL1Reader
from matplotlib.ticker import MultipleLocator
from tqdm import tqdm
import os
import numpy as np
from IPython import embed


class WFPlotter(Plotter):
    def plot(self, x, y):
        self.ax.plot(x, y, lw=0.1)

        self.ax.set_xlabel("Time (ns)")
        self.ax.set_ylabel("Amplitude (ADC)")

        self.ax.xaxis.set_major_locator(MultipleLocator(16))


class HistPlotter(Plotter):
    def plot(self, charge):
        mean = charge.mean()
        std = charge.std()
        normstd = std / mean
        text = "Mean={:.2f}\nSTD={:.2f}\nnormSTD={:.2f}".format(mean, std, normstd)

        self.ax.hist(charge, bins='auto')
        self.ax.text(0.96, 0.96, text, va='top', ha='right',
                     transform=self.ax.transAxes, fontsize=6)



def process(file):
    illumination = 50

    r1_path, _, _ = file.get_run_with_illumination(illumination, r1=True)
    dl1_path, _, _ = file.get_run_with_illumination(illumination, r1=False)
    poi = file.poi
    plot_dir = file.waveforms_plot_dir
    ff_path = file.ff_path

    with HDF5Reader(ff_path) as reader:
        df = reader.read("data")
        ff_m = df['ff_m'].values
        ff_c = df['ff_c'].values

    reader = TIOReader(r1_path)
    n_events = reader.n_events
    n_pixels = reader.n_pixels
    n_samples = reader.n_samples

    wfs = np.zeros((n_events, n_pixels, n_samples))
    desc = "Processing events"
    for wf in tqdm(reader, total=n_events, desc=desc):
        wfs[reader.index] = wf

    reader = DL1Reader(dl1_path)
    iev, pixel, charge_1d = reader.select_columns(['iev', 'pixel', 'charge'])
    charge_1d = (charge_1d - ff_c[pixel]) / ff_m[pixel]
    charge = np.zeros((n_events, n_pixels))
    charge[iev, pixel] = charge_1d

    x = np.arange(n_samples)

    p_wf = WFPlotter(switch_backend=True)
    p_wf.plot(x, wfs[:, poi].T)
    p_wf.save(os.path.join(plot_dir, "p{}.pdf".format(poi)))

    p_wf = WFPlotter()
    p_wf.plot(x, wfs.mean(0).T)
    p_wf.save(get_plot(os.path.join(plot_dir, "average.pdf")))

    p_hist = HistPlotter(switch_backend=True)
    p_hist.plot(charge[:, poi])
    p_hist.save(os.path.join(plot_dir, "hist.pdf"))


def main():
    process(d181010_LabSM_0MHz_100mV_TFNone())
    process(d181010_LabSM_0MHz_100mV_TFPchip())


if __name__ == '__main__':
    main()
