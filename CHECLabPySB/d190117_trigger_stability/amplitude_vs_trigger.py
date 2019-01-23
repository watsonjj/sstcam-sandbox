from CHECLabPySB.plotting.setup import Plotter
from CHECLabPySB.d190117_trigger_stability import *
from CHECLabPySB import get_data, get_plot, HDF5Reader
import numpy as np
import pandas as pd
import os
from matplotlib.backends.backend_pdf import PdfPages
from tqdm import tqdm
from matplotlib import pyplot as plt
from IPython import embed


class AmpVsTrigger(Plotter):
    def plot(self, x, y, label=None, **kwargs):
        self.ax.plot(x, y, '.', ms=1, label=label, alpha=0.7, **kwargs)

    def finish(self):
        self.ax.set_xlabel("Superpixel-Waveform Maximum (mV)")
        self.ax.set_ylabel("Trigger Counts in past minute")


class dAmpVsdTrigger(Plotter):
    def plot(self, x, y, label=None, **kwargs):
        self.ax.plot(x, y, '.', ms=1, label=label, **kwargs)

    def finish(self):
        self.ax.set_xlabel("Difference in Superpixel-Waveform Maximum (mV)")
        self.ax.set_ylabel("Difference in Trigger Counts")


def process(amplitude_path, trigger_path, output_dir, spoi):
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

    with HDF5Reader(trigger_path) as reader:
        df_trig = reader.read("data")

    df = pd.merge_asof(df_amp, df_trig,
                       on="t_cpu", by='superpixel',
                       direction='nearest',
                       suffixes=('_amp', '_trig'))

    gb = list(df.groupby("t_cpu"))
    diff = gb[-1][1]
    diff['amplitude_sp'] -= gb[0][1]['amplitude_sp'].values
    diff['count'] -= gb[0][1]['count'].values

    p_ampvstrig_all = AmpVsTrigger(switch_backend=True)
    superpixels = np.unique(df.loc[df['count'] < 200]['superpixel'])
    df_above = df.loc[df['superpixel'].isin(superpixels)]
    df_below = df.loc[~df['superpixel'].isin(superpixels)]
    x = df_above['amplitude_sp'].values
    y = df_above['count'].values
    p_ampvstrig_all.plot(x, y)
    x = df_below['amplitude_sp'].values
    y = df_below['count'].values
    p_ampvstrig_all.plot(x, y)
    p_ampvstrig_all.save(os.path.join(output_dir, "all.pdf"))
    p_ampvstrig_all.ax.set_ylim((0, 500))
    p_ampvstrig_all.save(os.path.join(output_dir, "all_zoom.pdf"))
    p_ampvstrig_all.ax.set_xlim((0, 200))
    p_ampvstrig_all.save(os.path.join(output_dir, "all_zoomx.pdf"))

    # p_ampvstrig_spoi = AmpVsTrigger(switch_backend=True)
    # for superpixel in tqdm(spoi, total=len(spoi)):
    #     df_sp = df.loc[df['superpixel'] == superpixel]
    #     label = "SP={}".format(superpixel)
    #     x = df_sp['amplitude_sp'].values
    #     y = df_sp['count'].values
    #     p_ampvstrig_spoi.plot(x, y, label=label)
    # p_ampvstrig_spoi.ax.set_xlim((0, 200))
    # p_ampvstrig_spoi.add_legend('best')
    # p_ampvstrig_spoi.save(os.path.join(output_dir, "spoi.pdf"))

    # p_diff = dAmpVsdTrigger(switch_backend=True)
    # x = diff['amplitude_sp'].values
    # y = np.abs(diff['count'].values)
    # p_diff.plot(x, y)
    # p_diff.save(os.path.join(output_dir, "dAmpVsdTrigger.pdf"))
    # p_diff.ax.set_ylim((-500, 10))
    # p_diff.save(os.path.join(output_dir, "dAmpVsdTrigger_zoom.pdf"))

    p_ampvstrig_sp = AmpVsTrigger(switch_backend=True)
    desc = "Plotting superpixels"
    with PdfPages(os.path.join(output_dir, "superpixels.pdf")) as pdf:
        for superpixel in tqdm(spoi, total=len(spoi), desc=desc):
            df_sp = df.loc[df['superpixel'] == superpixel]
            color = next(p_ampvstrig_sp.ax._get_lines.prop_cycler)['color']
            label = "SP={}".format(superpixel)

            x = df_sp['amplitude_sp'].values
            y = df_sp['count'].values
            p_ampvstrig_sp.plot(x, y, color=color)
            p_ampvstrig_sp.ax.set_title("SP {}".format(superpixel))
            p_ampvstrig_sp.finish()
            pdf.savefig(p_ampvstrig_sp.fig)
            p_ampvstrig_sp.ax.clear()




def process_file(file):
    name = file.__class__.__name__
    amplitude_path = get_data("d190117_trigger_stability/{}/amplitudes.h5".format(name))
    trigger_path = get_data("d190117_trigger_stability/{}/trigger.h5".format(name))
    output_dir = get_plot("d190117_trigger_stability/amp_vs_trig/{}".format(name))
    spoi = file.spoi
    process(amplitude_path, trigger_path, output_dir, spoi)


def main():
    files = [
        # d190111(),
        d190118(),
    ]
    [process_file(file) for file in files]


if __name__ == '__main__':
    main()