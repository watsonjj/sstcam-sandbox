from sstcam_sandbox import get_checs
from CHECLabPy.plotting.setup import Plotter
from TargetCalibSB.pedestal import PedestalTargetCalib
import numpy as np
from os.path import join


class Hist2D(Plotter):
    def plot(self, values, hits, clabel):
        masked = np.ma.masked_where(hits == 0, values)
        im = self.ax.imshow(
            masked, cmap="viridis", origin='lower', aspect='auto'
        )
        cbar = self.fig.colorbar(im)
        self.ax.patch.set(hatch='xx')
        self.ax.set_xlabel("Blockphase + Waveform position")
        self.ax.set_ylabel("Block")
        cbar.set_label(clabel)


class HistPlot(Plotter):
    def plot(self, hist, edges, mean, std):
        label = f"\nMean: {mean:.3f} StdDev: {std:.3f}"
        between = (edges[1:] + edges[:-1]) / 2
        self.ax.hist(
            between, bins=edges, weights=hist, label=label,
            histtype='step',
        )

    def finish(self):
        self.ax.set_xlabel("Residuals (ADC)")
        self.add_legend('best')


def process(pedestal_path, output_dir):
    pedestal = PedestalTargetCalib.from_tcal(pedestal_path)

    std_mean = np.mean(pedestal.std)
    std_std = np.std(pedestal.std)
    std_hist, std_edges = np.histogram(pedestal.std, bins=100)

    p_hist = HistPlot()
    p_hist.plot(std_hist, std_edges, std_mean, std_std)
    p_hist.save(join(output_dir, "hist.pdf"))

    p_hist2d_pedestal = Hist2D()
    p_hist2d_pedestal.plot(pedestal.pedestal[0], pedestal.hits[0], "Pedestal Mean (ADC)")
    p_hist2d_pedestal.save(join(output_dir, "hist2d_mean.pdf"))

    p_hist2d_std = Hist2D()
    p_hist2d_std.plot(pedestal.std[0], pedestal.hits[0], "Pedestal Stddev (ADC)")
    p_hist2d_std.save(join(output_dir, "hist2d_std.pdf"))


def main():
    pedestal_path = get_checs("d181203_erlangen/pedestal/Pedestal_10deg_ped.tcal")
    output_dir = get_checs("d181203_erlangen/pedestal/Pedestal_10deg_r0")
    process(pedestal_path, output_dir)

    pedestal_path = get_checs("d181203_erlangen/pedestal/Pedestal_15deg_ped.tcal")
    output_dir = get_checs("d181203_erlangen/pedestal/Pedestal_15deg_r0")
    process(pedestal_path, output_dir)

    pedestal_path = get_checs("d181203_erlangen/pedestal/Pedestal_23deg_ped.tcal")
    output_dir = get_checs("d181203_erlangen/pedestal/Pedestal_23deg_r0")
    process(pedestal_path, output_dir)

    pedestal_path = get_checs("d181203_erlangen/pedestal/Pedestal_30deg_ped.tcal")
    output_dir = get_checs("d181203_erlangen/pedestal/Pedestal_30deg_r0")
    process(pedestal_path, output_dir)

    pedestal_path = get_checs("d181203_erlangen/pedestal/Pedestal_40deg_ped.tcal")
    output_dir = get_checs("d181203_erlangen/pedestal/Pedestal_40deg_r0")
    process(pedestal_path, output_dir)


if __name__ == '__main__':
    main()
