from sstcam_simulation import Camera, PhotoelectronSource, SSTCameraMapping
from sstcam_simulation.camera.spe import SiPMGentileSPE
from CHECLabPy.plotting.setup import Plotter
from sstcam_sandbox import get_plot
import numpy as np
from tqdm import trange
from IPython import embed
from matplotlib import ticker


class SpectrumPlot(Plotter):
    pass
    # def plot(self, pe, label):
    #     self.ax.hist(x, y, label=label)

    # def finish(self):
    #     # self.ax.set_yscale("log")
    #     loc = ticker.MultipleLocator(base=1.0)
    #     self.ax.xaxis.set_major_locator(loc)
    #     self.ax.set_xlim(0, 6)
    #     self.ax.set_ylabel("Probability")
    #     self.add_legend('best')


def main():
    spectrum = SiPMGentileSPE(opct=0.2, normalise_x=False)
    camera = Camera(
        photoelectron_spectrum=spectrum,
        mapping=SSTCameraMapping(n_pixels=1)
    )
    n_events = 200000

    source = PhotoelectronSource(camera=camera)
    pe1 = []
    pe50 = []
    for iev in trange(n_events):
        pe1.append(source.get_uniform_illumination(20, 1).charge.sum())
        pe50.append(source.get_uniform_illumination(20, 20).charge.sum())
    pe1 = np.array(pe1)
    pe50 = np.array(pe50)

    # embed()

    plot = SpectrumPlot(sidebyside=True)
    plot.ax.hist(pe1, bins=70, histtype='step', label=f"λ = 1, Average Charge Per Event = {pe1.mean():.2f} f.c.")
    plot.ax.hist(pe50, bins=70, histtype='step', label=f"λ = 20, Average Charge Per Event = {pe50.mean():.2f} f.c.")
    # plot.ax.set_yscale('log')
    plot.ax.set_xlabel("Charge Per Event (f.c.)")
    plot.ax.set_ylabel("Number of Events")
    plot.add_legend('best')
    plot.save(get_plot("d201029_sipm_calib_doc/charge_mc.pdf"))

    spectrum = SiPMGentileSPE(opct=0.2, normalise_x=True)
    camera = Camera(
        photoelectron_spectrum=spectrum,
        mapping=SSTCameraMapping(n_pixels=1)
    )
    n_events = 200000

    source = PhotoelectronSource(camera=camera)
    pe1 = []
    pe50 = []
    for iev in trange(n_events):
        pe1.append(source.get_uniform_illumination(20, 1).charge.sum())
        pe50.append(source.get_uniform_illumination(20, 20).charge.sum())
    pe1 = np.array(pe1)
    pe50 = np.array(pe50)

    # embed()

    plot = SpectrumPlot(sidebyside=True)
    plot.ax.hist(pe1, bins=70, histtype='step', label=f"λ = 1, Average Charge Per Event = {pe1.mean():.2f} p.e.")
    plot.ax.hist(pe50, bins=70, histtype='step', label=f"λ = 20, Average Charge Per Event = {pe50.mean():.2f} p.e.")
    # plot.ax.set_yscale('log')
    plot.ax.set_xlabel("Charge Per Event (p.e.)")
    plot.ax.set_ylabel("Number of Events")
    plot.add_legend('best')
    plot.save(get_plot("d201029_sipm_calib_doc/charge_pe.pdf"))


if __name__ == '__main__':
    main()
