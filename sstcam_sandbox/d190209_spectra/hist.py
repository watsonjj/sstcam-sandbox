from sstcam_sandbox.plotting.setup import Plotter
from sstcam_sandbox import get_plot
from sstcam_sandbox.d190209_spectra.spe_numba import mapm
import numpy as np
from IPython import embed
from scipy.stats import poisson
from scipy.interpolate import PchipInterpolator
from matplotlib.ticker import FuncFormatter


class xyPlotter(Plotter):
    def plot(self, x, y, params):
        y /= np.sum(y)
        samples = np.random.choice(x, 20000, p=y)
        hist, _, _ = self.ax.hist(samples, bins=100)
        y *= (hist.max() / y.max())
        self.ax.plot(x, y)

        x = np.arange(5, dtype=np.float64)
        y = poisson.pmf(x, params['lambda_'])
        # embed()
        x *= params['spe']
        y *= (hist.max() / y.max())
        pchip = PchipInterpolator(x, y, axis=0, extrapolate=None)
        x = np.linspace(x.min(), x.max(), 1000)
        y = pchip(x)
        # self.ax.plot(x, y)

        # self.ax.set_yscale('log')
        # self.ax.get_yaxis().set_major_formatter(
        #     FuncFormatter(lambda yl, _: '{:g}'.format(yl)))


kwargs = dict(
    norm=1,
    eped=0,
    eped_sigma=0.4,
    spe=3.4,
    spe_sigma=0,
    lambda_=0.5,
)


def main():
    x = np.linspace(-2, 15, 300000, dtype=np.double)
    y = mapm(x, **kwargs)

    p = xyPlotter()
    p.plot(x, y, kwargs)
    p.ax.set_xlabel("Charge (AU)")
    p.ax.set_ylabel("Counts")
    p.save(get_plot("d190209_spectra/hist.pdf"))


if __name__ == '__main__':
    main()
