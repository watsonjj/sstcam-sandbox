from CHECLabPySB import get_data, get_plot
from CHECLabPy.core.io import HDF5Reader
from CHECLabPy.plotting.setup import Plotter


class MeanPlot(Plotter):
    def plot(self, vped, mean, label):
        self.ax.plot(vped, mean, label=label)

    def finish(self):
        self.ax.set_xlabel("VPED")
        self.ax.set_ylabel("Residuals Mean (Pedestal-subtracted ADC)")
        self.add_legend("best")


class StdPlot(Plotter):
    def plot(self, vped, std, label):
        self.ax.plot(vped, std, label=label)

    def finish(self):
        self.ax.set_xlabel("VPED")
        self.ax.set_ylabel("Residuals StdDev (Pedestal-subtracted ADC)")
        self.add_legend("best")


def main():
    paths = dict(
        before_25deg=get_data("d191128_pedestal_lab/residuals_self_vs_vped/before_25deg.h5"),
        before_35deg=get_data("d191128_pedestal_lab/residuals_self_vs_vped/before_35deg.h5"),
        c440pF_25deg=get_data("d191128_pedestal_lab/residuals_self_vs_vped/after_25deg.h5"),
        c440pF_35deg=get_data("d191128_pedestal_lab/residuals_self_vs_vped/after_35deg.h5"),
        c100pF_25deg=get_data("d191128_pedestal_lab/residuals_self_vs_vped/100pF_25deg.h5"),
        c100pF_35deg=get_data("d191128_pedestal_lab/residuals_self_vs_vped/100pF_35deg.h5"),
        c100pF_1k_25deg=get_data("d191128_pedestal_lab/residuals_self_vs_vped/100pF_1k_25deg.h5"),
        c200pF_25deg=get_data("d191128_pedestal_lab/residuals_self_vs_vped/200pF_25deg.h5"),
    )

    p_mean = MeanPlot()
    p_std = StdPlot()

    for label, path in paths.items():
        with HDF5Reader(path) as reader:
            df = reader.read("data")
            df = df.set_index("vped").sort_index()

        vped = df.index.values
        mean = df['mean'].values
        std = df['std'].values

        p_mean.plot(vped, mean, label)
        p_std.plot(vped, std, label)

    p_mean.save(get_plot(f"d191128_pedestal_lab/residuals_self/mean.pdf"))
    p_std.save(get_plot(f"d191128_pedestal_lab/residuals_self/std.pdf"))


if __name__ == '__main__':
    main()
