from sstcam_simulation.camera.spe import SiPMGentileSPE
from CHECLabPy.plotting.setup import Plotter
from sstcam_sandbox import get_plot
from matplotlib import ticker


class SpectrumPlot(Plotter):
    def plot(self, x, y, label):
        self.ax.plot(x, y, label=label)

    def finish(self):
        # self.ax.set_yscale("log")
        loc = ticker.MultipleLocator(base=1.0)
        self.ax.xaxis.set_major_locator(loc)
        self.ax.set_xlim(0, 6)
        self.ax.set_ylabel("Probability")
        self.add_legend('best')


def main():
    plot = SpectrumPlot(sidebyside=True)
    spectrum = SiPMGentileSPE(opct=0.2, normalise_x=False)
    plot.plot(spectrum.x, spectrum.pdf, label=f"OCT 20%, Average = {spectrum.average:.2f} f.c.")
    spectrum = SiPMGentileSPE(opct=0.4, normalise_x=False)
    plot.plot(spectrum.x, spectrum.pdf, label=f"OCT 40%, Average = {spectrum.average:.2f} f.c.")
    plot.ax.set_xlabel("Number of Fired Microcells (f.c.)")
    plot.save(get_plot("d201029_sipm_calib_doc/spectrum_mc.pdf"))

    plot = SpectrumPlot(sidebyside=True)
    spectrum = SiPMGentileSPE(opct=0.2, normalise_x=True)
    plot.plot(spectrum.x, spectrum.pdf, label=f"OCT 20%, Average = {spectrum.average:.2f} p.e.")
    spectrum = SiPMGentileSPE(opct=0.4, normalise_x=True)
    plot.plot(spectrum.x, spectrum.pdf, label=f"OCT 40%, Average = {spectrum.average:.2f} p.e.")
    plot.ax.set_xlabel("Photoelectrons (p.e.)")
    plot.save(get_plot("d201029_sipm_calib_doc/spectrum_pe.pdf"))


if __name__ == '__main__':
    main()
