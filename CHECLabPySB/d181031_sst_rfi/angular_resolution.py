from CHECLabPySB.plotting.setup import Plotter
from CHECLabPySB import get_data, get_plot
import numpy as np
from matplotlib.ticker import FuncFormatter


class AngResPlotter(Plotter):
    def plot(self, x, y, *args, **kwargs):
        self.ax.plot(x, y, *args, **kwargs)

    def finish(self):
        self.ax.set_xscale('log')
        self.ax.get_xaxis().set_major_formatter(
            FuncFormatter(lambda xl, _: '{:g}'.format(xl)))

        self.ax.set_xlabel("Energy (TeV)")
        self.ax.set_ylabel("Angular Resolution (deg)")

        # self.add_legend("best")

        self.ax.grid(alpha=0.4)


def main():
    x_gernot, y_gernot = np.loadtxt(get_data("d181031_sst_rfi/ang_res/gernot.txt"), unpack=True)
    x_2tel, y_2tel = np.loadtxt(get_data("d181031_sst_rfi/ang_res/dan_2tel.txt"), unpack=True)
    x_5tel, y_5tel = np.loadtxt(get_data("d181031_sst_rfi/ang_res/dan_5tel.txt"), unpack=True)
    x_req, y_req = np.loadtxt(get_data("d181031_sst_rfi/ang_res/South-50h-SST-AngRes.dat"), unpack=True)

    # x_gernot = np.log10(x_gernot)
    x_2tel = 10**x_2tel
    x_5tel = 10**x_5tel
    x_req = 10**x_req

    f = x_5tel > 1
    x_5tel = x_5tel[f]
    y_5tel = y_5tel[f]

    p_angres = AngResPlotter()
    p_angres.plot(x_req, y_req, '--', color='red', label="Requirement")
    p_angres.plot(x_gernot, y_gernot, 's-', ms=3, color='black', label="Gernot")
    # p_angres.plot(x_2tel, y_2tel, '.:', label="2 Tel")
    p_angres.plot(x_5tel, y_5tel, '.:', label="5 Tel")
    p_angres.save(get_plot("d181031_sst_rfi/ang_res.pdf"))


if __name__ == '__main__':
    main()
