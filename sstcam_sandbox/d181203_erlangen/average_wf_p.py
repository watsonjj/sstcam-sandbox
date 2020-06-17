from sstcam_sandbox.plotting.setup import Plotter
from sstcam_sandbox import HDF5Reader, get_plot
from sstcam_sandbox.d181203_erlangen.files.dc_tf import *
from sstcam_sandbox.d181203_erlangen.files.ac_tf import *
from sstcam_sandbox.d181203_erlangen.files.dynrange import *
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


def process(input_path, plot_path):
    with HDF5Reader(input_path) as reader:
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
    input_paths = file.r0_paths
    name = file.__class__.__name__
    input_path = get_data("d181203_erlangen/average_wf/{}.h5".format(name))
    output_path = get_plot("d181203_erlangen/average_wf/{}.pdf".format(name))
    process(input_path, output_path)


def main():
    files = [
        DC_TF_ExtSync_23deg(),
        DC_TF_HardSync_23deg(),
        AC_TF_23deg(),
        DynRange_23deg(),
    ]
    [process_file(f) for f in files]


if __name__ == '__main__':
    main()
