import os
import numpy as np
import pandas as pd
from CHECLabPy.plotting.setup import Plotter
from CHECLabPy.spectrum_fitters.gentile import pe_signal, K


class SPEHist(Plotter):
    def plot(self, hist, edges, between, x, y, y_nsb, opct):
        self.ax.hist(between, bins=edges, weights=hist, alpha=0.2)
        self.ax.plot(x, y, lw=0.5, label="Cherenkov, OPCT={:.2f}".format(opct))
        self.ax.plot(x, y_nsb, lw=0.5, label="NSB, OPCT={:.2f}".format(opct))

    def finish(self):
        self.ax.set_xlabel("Amplitude (p.e.)")
        self.ax.set_ylabel("N")
        self.add_legend()


def main():
    input_path = "/Volumes/gct-jason/data_checs/dynamicrange_180514/tf_pchip/spe_three.h5"
    file_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(file_dir, "outputs")

    dead = [677, 293, 27, 1925]

    store = pd.HDFStore(input_path)
    df = store['coeff_pixel']
    df_array = store['array_camera']
    df = df.loc[~df['pixel'].isin(dead)]
    df_mean = df.mean().to_dict()

    spe = df_mean['spe']
    norm = df_mean['norm0']

    d = dict(
        norm=1,
        eped=0,
        eped_sigma=0,
        spe=df_mean['spe'] / spe,
        spe_sigma=0.001,#df_mean['spe_sigma'] / spe,
        lambda_=0.02,
        opct=0.4,#df_mean['opct'],
        pap=0,
        dap=0
    )

    d_nsb = d.copy()
    d_nsb['pap'] = df_mean['pap']
    d_nsb['dap'] = df_mean['dap']

    hist = df_array.loc[0, 'hist'] / (norm * 100)
    edges = df_array.loc[0, 'edges'] / spe
    between = df_array.loc[0, 'between'] / spe

    x = np.linspace(0, 20, 1000)
    y = pe_signal(K, x[None, :], **d).sum(0)
    y_nsb = pe_signal(K, x[None, :], **d_nsb).sum(0)

    p_hist = SPEHist()
    p_hist.plot(hist, edges, between, x, y*25, y_nsb*25, d['opct'])
    output_path = os.path.join(output_dir, "checs_spe_spectrum.pdf")
    p_hist.save(output_path)

    output_path = os.path.join(output_dir, "checs_spe_spectrum.txt")
    np.savetxt(output_path, np.column_stack((x, y, y_nsb)))
    print("Created config : {}".format(output_path))


if __name__ == '__main__':
    main()
