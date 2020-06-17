from sstcam_sandbox.plotting.setup import Plotter
from sstcam_sandbox import get_plot
from sstcam_sandbox.d190209_spectra.spe_numba import sipm
import numpy as np
from tqdm import tqdm


class xyPlotter(Plotter):
    def plot(self, x, y):
        self.ax.plot(x, y)


kwargs = dict(
    norm=1,
    eped=0,
    eped_sigma=0.1,
    spe=1,
    spe_sigma=0.1,
    lambda_=10,
    opct=0.4,
    pap=0,
    dap=0,
)


def opct_f():
    opct_l = []
    val_l = []

    for opct in tqdm(np.linspace(0.000001, 0.95, 100)):
        kwargs_ = kwargs.copy()
        kwargs_['opct'] = opct
        x = np.linspace(-1, 300, 300000, dtype=np.double)
        y = sipm(x, **kwargs_)
        val = np.average(x, weights=y) / kwargs_['lambda_']
        opct_l.append(opct)
        val_l.append(val)

    p = xyPlotter()
    p.plot(np.array(opct_l), np.array(val_l))
    p.ax.set_xlabel("OPCT")
    p.ax.set_ylabel("Average / Lambda")
    p.save(get_plot("d190209_spectra/opct.pdf"))


def lambda_f():
    lambda_l = []
    val_l = []

    for lambda_ in tqdm(np.linspace(1, 10, 100)):
        kwargs_ = kwargs.copy()
        kwargs_['lambda_'] = lambda_
        x = np.linspace(-1, 300, 300000, dtype=np.double)
        y = sipm(x, **kwargs_)
        val = np.average(x, weights=y) / kwargs_['lambda_']
        lambda_l.append(lambda_)
        val_l.append(val)

    p = xyPlotter()
    p.plot(np.array(lambda_l), np.array(val_l))
    p.ax.set_xlabel("Lambda")
    p.ax.set_ylabel("Average / Lambda")
    p.save(get_plot("d190209_spectra/lambda.pdf"))


def main():
    opct_f()
    lambda_f()




if __name__ == '__main__':
    main()
