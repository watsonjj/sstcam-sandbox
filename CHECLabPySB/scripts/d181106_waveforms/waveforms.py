from CHECLabPySB import get_plot
from CHECLabPySB.plotting.setup import Plotter
from CHECLabPySB.scripts.d181106_waveforms import *
from CHECLabPy.core.io import TIOReader
from matplotlib.ticker import MultipleLocator


class WFPlotter(Plotter):
    def plot(self, x, y):
        self.ax.plot(x, y, lw=0.1)

        self.ax.set_xlabel("Time (ns)")
        self.ax.set_ylabel("Amplitude (ADC)")

        self.ax.xaxis.set_major_locator(MultipleLocator(16))


def process(file):
    r1_path = file.get_run_with_illumination(20, r1=True)
    poi = file.poi

    reader = TIOReader(r1_path)
    n_events = reader.n_events
    n_pixels = reader.n_pixels
    n_samples = reader.n_samples

    wfs = np.zeros((n_events, n_pixels, n_samples))
    for iev, wf in enumerate(reader):
        wfs[iev] = wf

    x = np.arange(n_samples)

    p_wf = WFPlotter()
    p_wf.plot(x, wfs[:, poi].T)
    p_wf.save(get_plot(""))


def main():
    process(d181010_LabSM_0MHz_100mV_TFPchip())


if __name__ == '__main__':
    main()
