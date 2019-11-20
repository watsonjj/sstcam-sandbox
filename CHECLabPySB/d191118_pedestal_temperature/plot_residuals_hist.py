from CHECLabPySB import get_data, get_plot
from CHECLabPy.core.io import HDF5Reader
from CHECLabPy.plotting.setup import Plotter
from IPython import embed


class HistPlot(Plotter):
    def plot(self, hist, edges, mean, std, label):
        label = label + f"\nMean: {mean:.3f} StdDev: {std:.3f}"
        between = (edges[1:] + edges[:-1]) / 2
        self.ax.hist(
            between, bins=edges, weights=hist, label=label,
            histtype='step',
        )

    def finish(self):
        self.ax.set_xlabel("Residuals (ADC)")
        self.add_legend('best')


def main():
    paths = dict(
        self=get_data("d191118_pedestal_temperature/d191118/residuals_self.h5"),
        single_31degree=get_data("d191118_pedestal_temperature/d191118/residuals_single_30.h5"),
        lookup=get_data("d191118_pedestal_temperature/d191118/residuals_lookup.h5"),
        interp=get_data("d191118_pedestal_temperature/d191118/residuals_interp.h5"),
        pchip=get_data("d191118_pedestal_temperature/d191118/residuals_pchip.h5"),
    )

    p_hist = dict()

    for label, path in paths.items():
        with HDF5Reader(path) as reader:
            df = reader.read("data")
            df = df.set_index("temperature_r0_primary").sort_index()

        for temperature, row in df.iterrows():
            hist = row['hist']
            edges = row['edges']
            mean = row['mean']
            std = row['std']

            if temperature not in p_hist:
                p_hist[temperature] = HistPlot()
                p_hist[temperature].ax.set_title(f"TM Primary Temperature = {temperature:.2f} °C")

            p_hist[temperature].plot(hist, edges, mean, std, label)


    for temperature, plot in p_hist.items():
        plot.save(get_plot(f"d191118_pedestal_temperature/d191118/hist/T{temperature:.2f}.pdf"))


if __name__ == '__main__':
    main()
