from CHECLabPySB import get_plot
from CHECLabPy.core.io import HDF5Reader
from CHECLabPy.plotting.setup import Plotter
from CHECLabPy.plotting.camera import CameraImage
from CHECLabPy.utils.mapping import get_clp_mapping_from_version, get_tm_mapping
from matplotlib import pyplot as plt
import matplotlib.colors as colors
import numpy as np
from scipy.interpolate import interp1d
from numpy.polynomial.polynomial import polyfit, polyval
from IPython import embed


class InternalVsExternal(Plotter):
    def plot(self, external, internal, intercept, gradient):
        color = self.ax._get_lines.get_next_color()
        self.ax.plot(external, internal, '.', alpha=0.1, color=color, ms=0.5)
        x_fit = np.linspace(external.min(), external.max(), 3)
        y_fit = polyval(x_fit, (intercept, gradient))
        self.ax.plot(x_fit, y_fit, color=color)

    def finish(self):
        plt.xlabel("External Temperature (°C)")
        plt.ylabel("TM Primary Temperature (°C)")


class FitPlot(Plotter):
    def __init__(self, mapping):
        super().__init__()

        self.fig = plt.figure(figsize=(20, 6))
        self.ax_c = self.fig.add_subplot(1, 3, 1)
        self.ax_m = self.fig.add_subplot(1, 3, 2)
        self.ci_c = self.create_image(
            mapping, ax=self.ax_c, clabel="Y-Intercept (°C)"
        )
        self.ci_m = self.create_image(
            mapping, ax=self.ax_m, clabel="Gradient (dInternalT/dExternalT)"
        )
        self.image_c = np.zeros(self.ci_c.xpix.size)
        self.image_m = np.zeros(self.ci_m.xpix.size)

    def plot(self, tm, intercept, gradient):
        self.image_c[tm] = intercept
        self.image_m[tm] = gradient

    def finish(self):
        self.ci_c.image = self.image_c
        self.ci_m.image = self.image_m

    @staticmethod
    def create_image(mapping, ax, clabel):
        ci = CameraImage.from_mapping(mapping, ax=ax)
        ci.add_colorbar(clabel, pad=0)
        ci.pixels.set_linewidth(0.2)
        ci.pixels.set_edgecolor('black')
        ci.image = np.zeros(ci.xpix.size)
        return ci


def main():
    with HDF5Reader("/Users/Jason/Downloads/tempdata/astri_db.h5") as reader:
        # df_astri = reader.read("WeatherStation_WS_EXTTMP")
        df_astri = reader.read("SQM_SQM_TEMP")
        df_astri = df_astri.set_index('timestamp').sort_index()
        df_astri = df_astri.query('(value != 0)').copy()
        df_astri['value'] = df_astri['value'].rolling('10min').mean()
        df_astri['hour'] = df_astri.index.astype('i8') * 1E-9 / (60 * 60)
        df_astri['gradient'] = df_astri['value'].diff() / df_astri['hour'].diff()

    with HDF5Reader("/Users/Jason/Downloads/tempdata/monitor.h5") as reader:
        df_monitor = reader.read("TM_T_PRI")
        df_monitor = df_monitor.set_index('t_cpu').sort_index()
        df_monitor = df_monitor.query(
            "(value != -1) & (value < 1000) & (value > -200)"
        ).copy()

        # Select monitor events with all 32 modules
        period_1s = df_monitor.index.to_period('1S')
        iunit_32 = df_monitor.groupby(period_1s).count()['value'] == 32
        dt_32 = iunit_32[iunit_32].index
        df_monitor = df_monitor[period_1s.isin(dt_32)]

        for tm, group in df_monitor.groupby('iunit'):
            tm_mask = df_monitor['iunit'] == tm
            df_monitor.loc[tm_mask, 'value'] = group['value'].rolling('3min').mean()
            hour = group.index.astype('i8') * 1E-9 / (60 * 60)
            df_monitor.loc[tm_mask, 'hour'] = hour
            diff = np.diff(group['value'], prepend=np.nan) / np.diff(hour, prepend=np.nan)
            df_monitor.loc[tm_mask, 'gradient'] = diff
        df_monitor = df_monitor.loc[np.abs(df_monitor['gradient']) <= 2]

    interp_f = interp1d(df_astri['hour'], df_astri['value'])
    df_monitor['external'] = interp_f(df_monitor['hour'])
    df_monitor = df_monitor.loc[df_monitor['external'] < 30]

    p_temp = InternalVsExternal()
    p_camera = FitPlot(get_tm_mapping(get_clp_mapping_from_version("1.1.0")))
    for tm, group in df_monitor.groupby('iunit'):
        external = group['external'].values
        internal = group['value'].values
        intercept, gradient = polyfit(external, internal, deg=1)
        p_temp.plot(external, internal, intercept, gradient)
        p_camera.plot(tm, intercept, gradient)
    p_temp.save(get_plot(f"d191118_pedestal_temperature/internal_vs_external.png"), dpi=1000)
    p_camera.save(get_plot(f"d191118_pedestal_temperature/internal_vs_external_fit.pdf"))


if __name__ == '__main__':
    main()
