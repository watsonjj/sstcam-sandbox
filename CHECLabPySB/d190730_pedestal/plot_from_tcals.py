from CHECLabPy.plotting.setup import Plotter
from CHECLabPy.plotting.camera import CameraImage
from CHECLabPy.core.io import HDF5Writer
from CHECLabPySB import get_data, get_plot
from CHECLabPySB.d190730_pedestal import all_files
from target_calib import PedestalArrayReader
import numpy as np
import pandas as pd
from tqdm import tqdm
from IPython import embed
from matplotlib.ticker import FuncFormatter


class Hist(Plotter):
    def plot(self, values):
        self.ax.hist(values, bins=1000, density=True)
        self.ax.set_yscale('log')


def process(name, tcal_path):
    ped_reader = PedestalArrayReader(tcal_path)
    hits_tcal = np.array(ped_reader.GetHits())
    std_tcal = np.array(ped_reader.GetStdDev())

    mask = (hits_tcal < 6) | np.isnan(std_tcal)
    std_tcal = np.ma.masked_array(std_tcal, mask=mask)

    embed()

    # std_values = std_tcal.compressed()
    # std_pix = std_tcal.mean((2, 3)).ravel()
    std_max_pix = std_tcal.max((2, 3)).ravel()

    # p_hist = Hist()
    # p_hist.plot(std_values)
    # p_hist.save(get_plot(f"d190730_pedestal/plot_from_tcals/hist/{name}.png"))
    #
    # p_ci = CameraImage.from_camera_version("1.1.0")
    # p_ci.image = std_pix
    # p_ci.add_colorbar()
    # p_ci.save(get_plot(f"d190730_pedestal/plot_from_tcals/camera/{name}.png"))

    p_ci = CameraImage.from_camera_version("1.1.0")
    p_ci.image = std_max_pix
    p_ci.add_colorbar()
    p_ci.save(get_plot(f"d190730_pedestal/plot_from_tcals/camera_max/{name}.png"))


def main():
    for file in tqdm(all_files):
        process(file.name, file.tcal)


if __name__ == '__main__':
    main()
