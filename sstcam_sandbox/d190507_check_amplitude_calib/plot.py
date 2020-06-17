from sstcam_sandbox import get_data, get_plot
from CHECLabPy.core.io import HDF5Reader
from CHECLabPy.plotting.setup import Plotter
import numpy as np
from datetime import datetime
from IPython import embed


class Plot(Plotter):
    def __init__(self):
        super().__init__()
        self.ax_temp = self.ax.twinx()

    def plot(self, datetime, nudge, temperature):
        color_nudge = next(self.ax._get_lines.prop_cycler)['color']
        color_temp = next(self.ax._get_lines.prop_cycler)['color']

        self.ax.plot(datetime, nudge, 'x', color=color_nudge)
        self.ax_temp.plot(datetime, temperature, 'x', color=color_temp)

        self.ax.set_ylim(-25, 25)
        self.ax_temp.set_ylim(15, 20)

        self.ax.set_xlabel("Datetime")
        self.ax.set_ylabel("Dac Nudge", color=color_nudge)
        self.ax_temp.set_ylabel("Average Temeperature (start of run)", color=color_temp)

        self.ax.tick_params(axis='y', labelcolor=color_nudge)
        self.ax_temp.tick_params(axis='y', labelcolor=color_temp)

        self.fig.autofmt_xdate()


def main():
    path = get_data("d190507_check_amplitude_calib/data.h5")
    output_path = get_plot("d190507_check_amplitude_calib/plot.pdf")
    with HDF5Reader(path) as reader:
        df = reader.read('data')

    df = df.sort_values('t_cpu')
    datetime = df['t_cpu'].values
    nudge = df['nudge'].values
    temperature = df['temperature'].values

    p = Plot()
    p.plot(datetime, nudge, temperature)
    p.save(output_path)


if __name__ == '__main__':
    main()