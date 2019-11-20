from CHECLabPySB import get_data, get_plot
from CHECLabPy.core.io import HDF5Reader
from CHECLabPy.plotting.setup import Plotter


class ValueVsTemp(Plotter):
    def plot(self, temperature, mean, std, label):
        caps = self.ax.errorbar(
            temperature, mean, yerr=std,
            linestyle='', capsize=1, elinewidth=0.5, fmt='.', markersize=1,
            label=label
        )
        for cap in caps[1]:
            cap.set_markeredgewidth(0.5)

    def finish(self):
        self.ax.set_xlabel("TM Primary Temperature (°C)")
        self.ax.set_ylabel("Change in ADC")
        self.add_legend("best")


class SpreadVsTemp(Plotter):
    def plot(self, temperature, mean, std):
        caps = self.ax.errorbar(
            temperature, mean, yerr=std,
            linestyle='', capsize=1, elinewidth=0.5, fmt='.', markersize=1,
        )
        for cap in caps[1]:
            cap.set_markeredgewidth(0.5)

    def finish(self):
        self.ax.set_xlabel("TM Primary Temperature (°C)")
        self.ax.set_ylabel("ADC Spread")
        # self.add_legend("best")


def main():
    path = get_data(f"d191118_pedestal_temperature/d191118/adc_vs_temperature.h5")

    with HDF5Reader(path) as reader:
        df = reader.read("data")
        df = df.set_index("temperature").sort_index()

    temperature = df.index.values
    delta_mean = df['delta_mean'].values
    delta_std = df['delta_std'].values
    delta_channel_mean = df['delta_channel_mean'].values
    delta_channel_std = df['delta_channel_std'].values
    spead_mean = df['spread_mean'].values
    spread_std = df['spread_std'].values

    p_delta = ValueVsTemp()
    p_delta.plot(temperature, delta_mean, delta_std, "TM")
    p_delta.plot(temperature, delta_channel_mean, delta_channel_std, "Channel 0")
    p_delta.save(get_plot(f"d191118_pedestal_temperature/d191118/delta_vs_temp.pdf"))

    # p_delta = ValueVsTemp()
    # p_delta.plot(temperature, delta_channel_mean, delta_channel_std)
    # p_delta.save(get_plot(f"d191118_pedestal_temperature/d191118/delta_channel_vs_temp.pdf"))

    p_delta = SpreadVsTemp()
    p_delta.plot(temperature, spead_mean, spread_std)
    p_delta.save(get_plot(f"d191118_pedestal_temperature/d191118/spread_vs_temp.pdf"))


if __name__ == '__main__':
    main()
