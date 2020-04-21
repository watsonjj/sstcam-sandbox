from CHECLabPySB import get_data, get_plot
from CHECLabPy.plotting.setup import Plotter
import pickle
import pandas as pd
from matplotlib.ticker import FuncFormatter
import datetime
import numpy as np
from matplotlib import pyplot as plt
from IPython import embed


class Timeseries(Plotter):
    def plot(self, x, y):
        self.ax.plot(x, y)

    def set_log_x(self):
        self.ax.set_xscale('log')
        self.ax.get_xaxis().set_major_formatter(
            FuncFormatter(lambda x, _: '{:g}'.format(x)))

    def set_log_y(self):
        self.ax.set_yscale('log')
        self.ax.get_yaxis().set_major_formatter(
            FuncFormatter(lambda y, _: '{:g}'.format(y)))


def main():
    path = get_data("d200122_pointing/draco_pointing_assessment_ghost_supr1.pkl")
    # path = get_data("d200122_pointing/draco_pointing_assessment_ghost_supr2.pkl")
    # path = get_data("d200122_pointing/draco_pointing_assessment_ghost_supr1_sim.pkl")
    with open(path, 'rb') as file:
        df = pd.DataFrame(pickle.load(file))
        # Fix for incorrect time storage (https://github.com/sstcam/SSDAQ/issues/92)
        df['t_cpu'] = (pd.to_datetime(df['unixtime'].values * 1e9)
                       .tz_localize("UTC")
                       .tz_convert("Europe/Berlin")
                       .tz_localize(None))

        # df.loc[((df['t_cpu'] < '2019-05-09 01:30') & (df['sep'] > 500)), 'sep'] = np.nan
        df = df.set_index("t_cpu")

    x = df.index.values
    y = df['sep'].values
    rolling_std = df.rolling('60s', min_periods=5).std()['sep'].values
    rolling_std /= df.rolling('60s', min_periods=5).count()['sep'].values

    # embed()

    p_ts = Timeseries()
    p_ts.plot(x, y)
    p_ts.ax.set_xlabel("Time")
    p_ts.ax.set_ylabel("Pointing Offset (arcseconds)")
    p_ts.set_log_y()
    p_ts.save(get_plot("d200122_pointing/ts_sep.pdf"))

    p_ts = Timeseries()
    p_ts.plot(x, rolling_std)
    p_ts.ax.set_xlabel("Time")
    p_ts.ax.set_ylabel("Rolling StdDev (1 minute) (arcseconds)")
    p_ts.set_log_y()
    # p_ts.ax.axhline(60, color='red')
    # p_ts.ax.axhline(20, color='blue')
    p_ts.save(get_plot("d200122_pointing/ts_std.pdf"))


if __name__ == '__main__':
    main()