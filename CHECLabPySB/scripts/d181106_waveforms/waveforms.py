from CHECLabPySB import get_plot
from CHECLabPySB.plotting.setup import Plotter
from CHECLabPySB.scripts.d181106_waveforms import *
from CHECLabPy.core.io import TIOReader


class WFPlotter(Plotter):
    def plot(self, x, y):
        self.ax.plot(x, y.T)




def process(file):
    r1_path = file.get_run_with_illumination(20, r1=True)
    reader = TIOReader(r1_path)
    n_events = reader.n_events
    n_pixels = reader.n_pixels
    n_samples = reader.n_samples

    wfs = np.zeros((n_events, n_pixels, n_samples))
    for iev, wf in enumerate(reader):
        wfs[iev] = wf





def main():
    process(d181010_LabSM_0MHz_100mV_TFPchip())


if __name__ == '__main__':
    main()
