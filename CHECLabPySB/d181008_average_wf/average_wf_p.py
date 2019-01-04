from CHECLabPySB.plotting.setup import Plotter
from CHECLabPySB import HDF5Reader
from CHECLabPySB.d181008_average_wf import *
from matplotlib.ticker import MultipleLocator
import numpy as np
from IPython import embed


class Waveform(Plotter):
    def plot(self, df, ifile):
        df_event = df.loc[df['ifile'] == ifile]
        x = df_event['isam']
        y = df_event['wf']
        self.ax.plot(x, y, 'black', lw=0.1)

        self.ax.set_xlabel("Time (ns)")
        self.ax.set_ylabel("Amplitude (ADC)")

        self.ax.xaxis.set_major_locator(MultipleLocator(16))


def process(data_path, plot_path):
    with HDF5Reader(data_path) as reader:
        df = reader.read("data")
        n_files = reader.read_metadata()['n_files']

    n_samples = df['isam'].max() + 1
    nan = df.groupby('ifile').count()['wf'] < n_samples
    nan_where = np.where(~nan)[0]
    df = df.loc[df['ifile'].isin(nan_where)]

    p_wf = Waveform(sidebyside=True)

    for ifile in range(n_files):

        # df_event = df.loc[df['ifile'] == ifile]
        # y = df_event['wf'].values
        # file = df_event['file'].values[0]
        # print(file, y.std())

        p_wf.plot(df, ifile)

    # embed()

    p_wf.save(plot_path)


def process_file(file):
    data_path = file.data_path
    plot_path = file.plot_path
    process(data_path, plot_path)


def main():
    files = [
        d180514_DynRange_TFPoly(),
        d181004_DynRange_SM_TFNone(),
    ]
    [process_file(f) for f in files]


if __name__ == '__main__':
    main()
