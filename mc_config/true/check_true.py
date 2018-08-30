import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.collections import LineCollection
import seaborn as sns
from CHECLabPy.core.io import DL1Reader
from CHECLabPy.plotting.setup import Plotter
from CHECLabPy.plotting.camera import CameraImage
from numpy.polynomial.polynomial import polyfit, polyval
from IPython import embed


class PixelScatter(Plotter):
    def __init__(self, xlabel='', ylabel='', zlabel='', title=''):
        super().__init__()

        self.xlabel = xlabel
        self.ylabel = ylabel
        self.zlabel = zlabel
        self.title = title

        self.df_list = []

    def plot(self, x, y, z):
        # y = 1 / np.sqrt(y)

        params = polyfit(x, y, [0, 2])

        # y /= polyval(x, params)
        # y *= polyval(0, params)
        # embed()

        cm = plt.cm.get_cmap('viridis')
        sc = self.ax.scatter(x, y, c=z, cmap=cm, s=0.5)

        xf = np.linspace(x.min(), x.max(), 10)
        yf = polyval(xf, params)
        self.ax.plot(xf, yf)

        cb = self.fig.colorbar(sc)
        cb.set_label(self.zlabel)

        self.ax.set_title(self.title)
        self.ax.set_xlabel(self.xlabel)
        self.ax.set_ylabel(self.ylabel)

        return params/polyval(0, params)


# path = "/Volumes/gct-jason/mc_checs/dynamic_range/0mhz/cc/Run43495_dl1.h5"
# path = "/Volumes/gct-jason/mc_checs/no_noise/Run43489_dl1.h5"
path = "/Volumes/gct-jason/mc_checs/no_noise/Run43489_flat_dl1.h5"


r = DL1Reader(path)
m = r.mapping
poi = np.arange(2048)#m.loc[m['row'] == 47//2]['pixel'].values
pixel, measured, true = r.select_columns(['pixel', 'charge', 'mc_true'])
xpix = m['xpix']
ypix = m['ypix']
dist = np.sqrt(xpix ** 2 + ypix ** 2)

measured_p = measured.values.reshape((1000, 2048)).mean(0)
true_p = true.values.reshape((1000, 2048)).mean(0)

p_mvt = PixelScatter("Measured", "True", "Distance from camera center")
p_dvt = PixelScatter("Distance from camera center", "True", "Measured")
p_dvm = PixelScatter("Distance from camera center", "Measured", "True")

# p_mvt.plot(measured_p, true_p, dist)
calib_params = p_dvt.plot(dist, true_p, measured_p)
# p_dvm.plot(dist, measured_p, true_p)

p_mvt.save("mvt.pdf")
p_dvt.save("dvt.pdf")
p_dvm.save("dvm.pdf")

xpix = m['xpix'].values
ypix = m['ypix'].values
dist = np.sqrt(xpix ** 2 + ypix ** 2)
f = polyval(dist, calib_params)
print(calib_params)

p_f = CameraImage.from_mapping(m)
p_f.image = f
p_f.add_colorbar()
p_f.save("f.pdf")

np.savetxt("illumination_correction_mc.txt", f)