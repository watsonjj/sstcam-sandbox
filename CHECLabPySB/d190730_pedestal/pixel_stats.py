from CHECLabPy.plotting.setup import Plotter
from CHECLabPySB import get_data, get_plot
from CHECLabPySB.d190730_pedestal import setup_cells
from CHECLabPy.core.io import HDF5Reader
import numpy as np
from IPython import embed


class LookupTable(Plotter):
    def plot(self, data, data_title=""):
        pixel_hits_0 = np.ma.masked_where(data == 0, data)

        im = self.ax.pcolor(pixel_hits_0, cmap="viridis",
                            edgecolors='white', linewidths=0.1)
        cbar = self.fig.colorbar(im)
        self.ax.patch.set(hatch='xx')
        self.ax.set_xlabel("Blockphase + Waveform position")
        self.ax.set_ylabel("Block")
        cbar.set_label(data_title)

        # self.ax.set_ylim(110, 120)


def main():
    with HDF5Reader(get_data("d190730_pedestal/ped.h5")) as reader:
        df = reader.read('data')

    df = setup_cells(df)
    std = df.groupby(['fblock', 'fbpisam'])['adc'].std()
    




    print(f"Min hits: {count.min()}")

    p_count = LookupTable()
    p_count.plot(count, "Counts")
    p_count.save(get_plot("d190730_pedestal/count.pdf"))

    p_mean = LookupTable()
    p_mean.plot(mean, "Mean")
    p_mean.save(get_plot("d190730_pedestal/mean.pdf"))

    p_std = LookupTable()
    p_std.plot(std, "Stddev")
    p_std.save(get_plot("d190730_pedestal/std.pdf"))


if __name__ == '__main__':
    main()
