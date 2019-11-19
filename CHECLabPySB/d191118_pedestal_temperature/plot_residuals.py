from CHECLabPySB import get_data, get_plot
from CHECLabPy.core.io import HDF5Reader
from CHECLabPy.plotting.setup import Plotter


class TemperatureComparison(Plotter):
    def plot(self, chamber, primary):
        self.ax.plot(chamber, primary)

    def finish(self):
        self.ax.set_xlabel("Chamber Temperature (°C)")
        self.ax.set_ylabel("TM Primary Temperature (°C)")
        self.add_legend("best")


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


class RelativeStdVsTemperature(Plotter):
    def plot(self, temperature, std, ref_std, label):
        self.ax.plot(temperature, std/ref_std, label=label)

    def finish(self):
        self.ax.set_xlabel("TM Primary Temperature (°C)")
        self.ax.set_ylabel("Relative StdDev")
        self.add_legend("best")


def main():
    paths = dict(
        self=get_data("d191118_pedestal_temperature/residuals_self.h5"),
        # single_20degree=get_data("d191118_pedestal_temperature/residuals_single_20.h5"),
        single_31degree=get_data("d191118_pedestal_temperature/residuals_single_30.h5"),
        # single_40degree=get_data("d191118_pedestal_temperature/residuals_single_40.h5"),
        lookup=get_data("d191118_pedestal_temperature/residuals_lookup.h5"),
        interp=get_data("d191118_pedestal_temperature/residuals_interp.h5"),
        pchip=get_data("d191118_pedestal_temperature/residuals_pchip.h5"),
    )

    p_mean = MeanVsTemperature()
    p_std = StdVsTemperature()
    p_relstd =RelativeStdVsTemperature()

    with HDF5Reader(paths['self']) as reader:
        df = reader.read("data")
        df = df.set_index("temperature_r0_primary").sort_index()
        # df = df.loc[df.index < 38]
        # df = df.loc[df.index != 23.72]
        ref_std = df['std'].values

    for label, path in paths.items():
        with HDF5Reader(path) as reader:
            df = reader.read("data")
            df = df.set_index("temperature_r0_primary").sort_index()
            # df = df.loc[df.index < 38]
            # df = df.loc[df.index != 23.72]

        temperature = df.index.values
        mean = df['mean'].values
        std = df['std'].values

        p_mean.plot(temperature, mean, label)
        p_std.plot(temperature, std, label)
        p_relstd.plot(temperature, std, ref_std, label)

    p_mean.save(get_plot(f"d191118_pedestal_temperature/mean.pdf"))
    p_std.save(get_plot(f"d191118_pedestal_temperature/std.pdf"))
    p_relstd.save(get_plot(f"d191118_pedestal_temperature/rel_std.pdf"))

    with HDF5Reader(paths['self']) as reader:
        df = reader.read("data")
        df = df.set_index("temperature_r0_chamber").sort_index()
        chamber = df.index.values
        primary = df['temperature_r0_primary'].values

    p_temp = TemperatureComparison()
    p_temp.plot(chamber, primary)
    p_temp.save(get_plot(f"d191118_pedestal_temperature/temp.pdf"))


if __name__ == '__main__':
    main()
