import os
import numpy as np
import pandas as pd
from CHECLabPy.plotting.setup import Plotter
from scipy.stats import norm


class GainSpread(Plotter):
    def plot(self, spe):
        mean = np.mean(spe)
        std = np.std(spe)
        self.frac = std/mean

        x = np.linspace(spe.min(), spe.max(), 100)
        gaus = norm.pdf(x, mean, std)

        label = ("Mean: {:.3f}, StdDev: {:.3f}, Fractional Variation: {:.3f}"
                 .format(mean, std, self.frac))

        self.ax.hist(spe, bins='auto', normed=True)
        self.ax.plot(x, gaus, label=label)

    def finish(self):
        self.ax.set_xlabel("SPE Value (mV ns)")
        self.ax.set_ylabel("Density")
        self.add_legend()

    def save(self, output_path):
        super().save(output_path)
        np_path = output_path.replace('.pdf', '.npy')
        rand = np.random.normal(1, self.frac, 2048)
        np.save(np_path, rand)

def main():
    input_path = "/Volumes/gct-jason/data_checs/dynamicrange_180514/tf_pchip/spe_three.h5"
    file_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(file_dir, "outputs")

    dead = [677, 293, 27, 1925]

    store = pd.HDFStore(input_path)
    df = store['coeff_pixel']
    df = df.loc[~df['pixel'].isin(dead)]
    spe = df['spe'].values

    p_hist = GainSpread()
    p_hist.plot(spe)
    output_path = os.path.join(output_dir, "checs_gain_variation.pdf")
    p_hist.save(output_path)


if __name__ == '__main__':
    main()
