import os
import numpy as np
import pandas as pd
from CHECLabPy.plotting.setup import Plotter
from scipy.stats import norm


class PedestalSpread(Plotter):
    def plot(self, eped_sigma):
        mean = np.mean(eped_sigma)
        std = np.std(eped_sigma)

        x = np.linspace(eped_sigma.min(), eped_sigma.max(), 100)
        gaus = norm.pdf(x, mean, std)

        label = ("Mean: {:.3f}, StdDev: {:.3f}, Fractional Variation: {:.3f}"
                 .format(mean, std, std/mean))

        self.ax.hist(eped_sigma, bins='auto', normed=True)
        self.ax.plot(x, gaus, label=label)

    def finish(self):
        self.ax.set_xlabel("Eped Sigma (mV ns)")
        self.ax.set_ylabel("Density")
        self.add_legend()


def main():
    input_path = "/Volumes/gct-jason/data_checs/dynamicrange_180514/tf_pchip/spe_three.h5"
    file_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(file_dir, "outputs")

    dead = [677, 293, 27, 1925]

    store = pd.HDFStore(input_path)
    df = store['coeff_pixel']
    df = df.loc[~df['pixel'].isin(dead)]
    eped_sigma = df['eped_sigma'].values

    p_hist = PedestalSpread()
    p_hist.plot(eped_sigma)
    output_path = os.path.join(output_dir, "checs_fadc_pedestal_variation.pdf")
    p_hist.save(output_path)


if __name__ == '__main__':
    main()
