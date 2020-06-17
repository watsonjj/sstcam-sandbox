from sstcam_sandbox import get_data, get_plot
from CHECLabPy.core.io import HDF5Reader
from CHECLabPy.plotting.setup import Plotter


class MeanVsTemperature(Plotter):
    def plot(self, temperature, mean, label):
        self.ax.plot(temperature, mean, label=label)

    def finish(self):
        self.ax.set_xlabel("TM Primary Temperature (°C)")
        self.ax.set_ylabel("Residuals Mean (Pedestal-subtracted ADC)")
        self.add_legend("best")


class StdVsTemperature(Plotter):
    def plot(self, temperature, std, label):
        self.ax.plot(temperature, std, label=label)

    def finish(self):
        self.ax.set_xlabel("TM Primary Temperature (°C)")
        self.ax.set_ylabel("Residuals StdDev (Pedestal-subtracted ADC)")
        self.add_legend("best")


def main():
    paths = dict(
        d191118_625Hz_interp=get_data("d191118_pedestal_temperature/d191118/residuals_interp.h5"),
        d191119_625Hz_interp=get_data("d191118_pedestal_temperature/d191119/residuals_interp.h5"),
        d191120_200Hz_interp=get_data("d191118_pedestal_temperature/d191120/residuals_interp.h5"),
    )

    p_mean = MeanVsTemperature()
    p_std = StdVsTemperature()

    for label, path in paths.items():
        with HDF5Reader(path) as reader:
            df = reader.read("data")
            df = df.set_index("temperature_r0_primary").sort_index()

        temperature = df.index.values
        mean = df['mean'].values
        std = df['std'].values

        p_mean.plot(temperature, mean, label)
        p_std.plot(temperature, std, label)

    p_mean.save(get_plot(f"d191118_pedestal_temperature/vs_day/mean.pdf"))
    p_std.save(get_plot(f"d191118_pedestal_temperature/vs_day/std.pdf"))


if __name__ == '__main__':
    main()
