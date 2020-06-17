from CHECLabPy.plotting.setup import Plotter
from sstcam_sandbox.d190730_pedestal import all_files
from target_calib import PedestalArrayReader
from astropy.io import fits
import numpy as np
from os.path import join
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


def process(input_path, output, poi):

    tm = poi // 64
    tmpix = poi % 64

    ped_reader = PedestalArrayReader(input_path)
    pedestal_tcal = np.array(ped_reader.GetPedestal())[tm, tmpix]
    hits_tcal = np.array(ped_reader.GetHits())[tm, tmpix]
    std_tcal = np.array(ped_reader.GetStdDev())[tm, tmpix]
    # header = fits.open(input_path)[0].header
    # n_samplesbp = int(header['MAXSAMPLESBP']) + 1
    # pedestal_tcal = pedestal_tcal[:, :n_samplesbp]
    # hits_tcal = hits_tcal[:, :n_samplesbp]
    # std_tcal = std_tcal[:, :n_samplesbp]

    print(f"Min hits: {hits_tcal.min()}")

    p_count = LookupTable()
    p_count.plot(hits_tcal, "Counts")
    p_count.save(join(output, "map_count.pdf"))

    p_mean = LookupTable()
    p_mean.plot(pedestal_tcal, "Mean")
    p_mean.save(join(output, "map_mean.pdf"))

    p_std = LookupTable()
    p_std.plot(std_tcal, "Stddev")
    p_std.save(join(output, "map_std.pdf"))


def main():
    for file in all_files:
        process(file.tcal, file.plot_dir, 30)


if __name__ == '__main__':
    main()
