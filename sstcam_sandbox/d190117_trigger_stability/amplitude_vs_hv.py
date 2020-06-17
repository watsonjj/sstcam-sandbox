from sstcam_sandbox.plotting.setup import Plotter
from sstcam_sandbox.d190117_trigger_stability import *
from sstcam_sandbox import get_data, get_plot, HDF5Reader
import numpy as np
import pandas as pd
import os
from matplotlib.backends.backend_pdf import PdfPages
from tqdm import tqdm, trange
from matplotlib import pyplot as plt
from IPython import embed


class AmpVsHV(Plotter):
    def plot(self, x, y, label=None, **kwargs):
        self.ax.plot(x, y, '.', ms=1, label=label, alpha=0.7, **kwargs)

    def finish(self):
        self.ax.set_xlabel("Superpixel Voltage (Volts)")
        self.ax.set_ylabel("Superpixel-Waveform Maximum (mV)")


def process(amplitude_path, hv_path, output_dir, spoi):
    with HDF5Reader(amplitude_path) as reader:
        df_amp = reader.read("data")
        mapping = reader.read_mapping()
        superpixels = mapping['superpixel'].values.astype(np.int)
        df_amp['superpixel'] = superpixels[df_amp['pixel']]
        df_amp = (df_amp
                  .drop(['amplitude', 'pixel'], axis=1)
                  .set_index('t_cpu')
                  .groupby([pd.Grouper(freq='60S'), 'superpixel'])
                  .mean()
                  .reset_index())

    with HDF5Reader(hv_path) as reader:
        df_hv = reader.read("data")
        # df_hv = (df_hv
        #           .set_index('t_cpu')
        #           .groupby([pd.Grouper(freq='387S'), 'superpixel'])
        #           .mean()
        #           .reset_index()
        #           )
        df_hv = (df_hv
                  .sort_values("t_cpu")
                 )

    df = pd.merge_asof(df_amp, df_hv,
                       on="t_cpu", by='superpixel',
                       direction='nearest',
                       suffixes=('_amp', '_trig'))

    p_ampvshv_all = AmpVsHV(switch_backend=True)
    x = df['amplitude_sp'].values
    y = df['hv'].values
    p_ampvshv_all.plot(x, y)
    p_ampvshv_all.save(os.path.join(output_dir, "all.pdf"))
    p_ampvshv_all.ax.set_ylim((50, 70))
    p_ampvshv_all.save(os.path.join(output_dir, "all_zoom.pdf"))
    # p_ampvshv_all.ax.set_xlim((0, 200))
    # p_ampvshv_all.save(os.path.join(output_dir, "all_zoomx.pdf"))

    df['tm'] = df['superpixel'] // 16
    df = df.loc[df['hv'] > 56]
    ymin = df['amplitude_sp'].min()
    ymax = df['amplitude_sp'].max()
    p_ampvshv_tm = AmpVsHV(switch_backend=True)
    with PdfPages(os.path.join(output_dir, "tm.pdf")) as pdf:
        for tm, group_tm in tqdm(df.groupby("tm"), total=32):
            for sp, group_sp in group_tm.groupby("superpixel"):
                color = next(p_ampvshv_tm.ax._get_lines.prop_cycler)['color']
                label = "SP={}".format(sp)
                x = group_sp['hv'].values
                y = group_sp['amplitude_sp'].values
                p_ampvshv_tm.plot(x, y, color=color, label=label)
                p_ampvshv_tm.ax.set_title("TM {}".format(tm))
            p_ampvshv_tm.finish()
            p_ampvshv_tm.add_legend(5)
            p_ampvshv_tm.ax.set_xlim((65, 70))
            p_ampvshv_tm.ax.set_ylim((ymin, ymax))
            pdf.savefig(p_ampvshv_tm.fig)
            p_ampvshv_tm.ax.clear()


def process_file(file):
    name = file.__class__.__name__
    amplitude_path = get_data("d190117_trigger_stability/{}/amplitudes.h5".format(name))
    hv_path = get_data("d190117_trigger_stability/{}/hv.h5".format(name))
    output_dir = get_plot("d190117_trigger_stability/amp_vs_hv/{}".format(name))
    spoi = file.spoi
    process(amplitude_path, hv_path, output_dir, spoi)


def main():
    files = [
        # d190111(),
        # d190118(),
        d190121(),
    ]
    [process_file(file) for file in files]


if __name__ == '__main__':
    main()