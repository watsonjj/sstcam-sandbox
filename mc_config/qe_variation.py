import os
import re
import numpy as np
import pandas as pd
from CHECLabPy.plotting.setup import Plotter
from scipy.stats import norm
from CHECLabPy.utils.files import read_runlist
from numpy.polynomial.polynomial import polyfit


class QESpread(Plotter):
    def plot(self, lambda_):
        mean = np.mean(lambda_)
        std = np.std(lambda_)

        x = np.linspace(lambda_.min(), lambda_.max(), 100)
        gaus = norm.pdf(x, mean, std)

        label = ("Mean: {:.3f}, StdDev: {:.3f}, Fractional Variation: {:.3f}"
                 .format(mean, std, std/mean))

        self.ax.hist(lambda_, bins=100, normed=True)
        self.ax.plot(x, gaus, label=label)

    def finish(self):
        self.ax.set_xlabel("Gradient of Lambda_ (p.e.) versus FW_Transmission")
        self.ax.set_ylabel("Density")
        self.add_legend()


def main():
    input_path = "/Volumes/gct-jason/data_checs/dynamicrange_180514/tf_pchip/spe_three.h5"
    runlist_path = "/Volumes/gct-jason/data_checs/dynamicrange_180514/tf_pchip/runlist.txt"
    file_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(file_dir, "outputs")

    dead = [677, 293, 27, 1925]

    store = pd.HDFStore(input_path)
    df = store['coeff_pixel']
    df = df.loc[~df['pixel'].isin(dead)]
    lambda_ = df['lambda_2'].values

    df_runs = read_runlist(runlist_path)
    df_runs['transmission'] = 1 / df_runs['fw_atten']

    meta_spe = store.get_storer('metadata').attrs.metadata
    n_spe_illuminations = meta_spe['n_illuminations']
    spe_files = meta_spe['files']
    n_pixels = np.unique(df['pixel']).size

    spe_transmission = []
    pattern = '(.+?)/Run(.+?)_dl1.h5'
    for path in spe_files:
        try:
            reg_exp = re.search(pattern, path)
            if reg_exp:
                run = int(reg_exp.group(2))
                spe_transmission.append(df_runs.loc[run]['transmission'])
        except AttributeError:
            print("Problem with Regular Expression, "
                  "{} does not match patten {}".format(path, pattern))
    np.array(spe_transmission)

    pix_lambda = np.zeros((n_spe_illuminations, n_pixels))
    for ill in range(n_spe_illuminations):
        key = "lambda_" + str(ill)
        lambda_ = df[['pixel', key]].sort_values('pixel')[key].values
        pix_lambda[ill] = lambda_

    c, m = polyfit(spe_transmission, pix_lambda, 1)

    p_hist = QESpread()
    p_hist.plot(m)
    output_path = os.path.join(output_dir, "checs_qe_variation.pdf")
    p_hist.save(output_path)


if __name__ == '__main__':
    main()
