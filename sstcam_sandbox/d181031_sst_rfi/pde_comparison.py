from sstcam_sandbox.plotting.setup import Plotter
from sstcam_sandbox import get_data, get_plot
import numpy as np
from IPython import embed


class PDEPlotter(Plotter):
    def plot(self, x, y, label):
        integral = np.trapz(y, x)
        label = label + "(Integral = {:.3f})".format(integral)
        self.ax.plot(x, y, label=label)

    def finish(self):
        self.add_legend("best")


def main():
    x_checs, y_checs = np.loadtxt(get_data("d181031_sst_rfi/pde/CHECS.dat"), unpack=True)
    x_prod3, y_prod3 = np.loadtxt(get_data("d181031_sst_rfi/pde/Prod3.dat"), unpack=True)
    x_prod4, y_prod4 = np.loadtxt(get_data("d181031_sst_rfi/pde/Prod4.dat"), unpack=True)

    integral_checs = np.trapz(y_checs, x_checs)
    integral_prod3 = np.trapz(y_prod3, x_prod3)
    print(integral_checs / integral_prod3)


    p_pde = PDEPlotter()
    p_pde.plot(x_checs, y_checs, label="CHEC-S")
    p_pde.plot(x_prod3, y_prod3, label="Prod3")
    p_pde.plot(x_prod4, y_prod4, label="Prod4")
    p_pde.save(get_plot("d181031_sst_rfi/pde.pdf"))

if __name__ == '__main__':
    main()
