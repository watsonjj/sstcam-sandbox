from sstcam_sandbox.plotting.setup import Plotter
from sstcam_sandbox import get_data, HDF5Reader, get_plot
from sstcam_sandbox.d190104_vped_pedestal_steps import *
import numpy as np
from target_calib import CalculateRowColumnBlockPhase, GetCellIDTCArray
from IPython import embed
import os
from matplotlib.ticker import MultipleLocator


def setup_cells(df):
    fci = df['fci'].values.astype(np.uint16)
    frow, fcolumn, fblockphase = CalculateRowColumnBlockPhase(fci)
    fblock = fcolumn * 8 + frow
    df['fblock'] = fblock
    df['fblockphase'] = fblockphase
    df['fbpisam'] = df['fblockphase'] + df['isam']

    cell = GetCellIDTCArray(fci, df['isam'].values.astype(np.uint16))
    row, column, blockphase = CalculateRowColumnBlockPhase(cell)
    block = column * 8 + row
    df['cell'] = cell
    df['block'] = block
    df['blockphase'] = blockphase

    df['iblock'] = (df['isam'] + df['fblockphase']) // 32

    return df


class DiffPlotter(Plotter):
    def plot(self, df_cell):
        df_iblock = df_cell.groupby(['amplitude', 'iblock']).sum().reset_index()
        sum_ = df_iblock['sum'].values
        sum2 = df_iblock['sum2'].values
        n = df_iblock['n'].values
        mean = sum_ / n
        std = np.sqrt((sum2 / n) - (mean ** 2))
        df_iblock['mean'] = mean
        df_iblock['std'] = std

        vped_list = []
        diff_list = []
        for vped, group in df_iblock.groupby('amplitude'):
            vped_list.append(vped)
            diff_list.append(np.diff(group['mean']))

        vped = np.array(vped_list)
        diff = np.array(diff_list)

        self.ax.plot(vped, diff)

        self.ax.set_xlabel("Vped")
        self.ax.set_ylabel("Diff")


class CellWaveform(Plotter):
    def plot(self, df_cell):

        u = np.unique(df_cell['amplitude'])
        v1200 = u[np.argmin(np.abs(u) - 1200)]
        df_1200 = df_cell.loc[df_cell['amplitude'] == v1200]
        x = df_1200['isam'].values
        y1200 = df_1200['mean'].values
        sort = np.argsort(x)
        x = x[sort]
        y1200 = y1200[sort]

        for vped, group in df_cell.groupby('amplitude'):
            x = group['isam'].values
            y = group['mean'].values
            yerr = group['std'].values

            sort = np.argsort(x)
            x = x[sort]
            y = y[sort]
            yerr = yerr[sort]

            y -= y1200

            y -= y.mean()
            # yerr /= y.mean()

            self.ax.errorbar(x, y, yerr=None)
            # self.ax.errorbar(x, y, yerr=yerr)

        # df_cell = df.loc[df['cell'] == cell]
        # df_isam = df_cell.groupby('isam').agg(
        #     {'r0': ['mean', 'std'], 'iblock': 'mean'}
        # )
        # df_block = df_cell.groupby('iblock').agg(
        #     {'r0': ['mean', 'std'], 'isam': ['mean', 'min', 'max']}
        # )
        #
        # x = df_isam.index.values
        # y = df_isam['r0']['mean'].values
        # yerr = df_isam['r0']['std'].values
        #
        # xb = df_block['isam']['mean'].values
        # yb = df_block['r0']['mean'].values
        # yberr = df_block['r0']['std'].values
        #
        # for _, row in df_block.iterrows():
        #     color = self.ax._get_lines.get_next_color()
        #     self.ax.axvline(row['isam']['min'], color=color, ls='--', alpha=0.7)
        #     self.ax.axvline(row['isam']['max'], color=color, ls='--', alpha=0.7)
        # self.ax.errorbar(xb, yb, yerr=yberr, color='red')
        # self.ax.errorbar(x, y, yerr=yerr, color='black')
        #
        # self.ax.set_xlabel("Position in waveform")
        # self.ax.set_ylabel("Amplitude (Raw ADC)")
        # # self.ax.set_title("Cell = {}".format(cell))

        self.ax.xaxis.set_major_locator(MultipleLocator(16))
        self.ax.set_ylim((-13, 6))


def process(input_path, output_dir, coi):
    with HDF5Reader(input_path) as reader:
        df = reader.read("data")

    df = setup_cells(df)

    df_cell = df.loc[df['cell'] == coi]

    # p_diff = DiffPlotter()
    # p_diff.plot(df_cell)
    # p_diff.save(os.path.join(output_dir, "diff.pdf"))

    p_wf = CellWaveform()
    p_wf.plot(df_cell)
    p_wf.save(os.path.join(output_dir, "cellwf.pdf"))


    # vpeds = np.unique(df_cell['amplitude'])
    # df_amp = df_cell.loc[df_cell['amplitude'] == vpeds[0]]
    # boundaries = df_amp.groupby('iblock').agg({'isam': ['min', 'max']})
    # boundaries = boundaries.as_matrix().ravel()[1:-1]
    # boundaries = boundaries.reshape((boundaries.size//2, 2))
    #
    # points = []
    # for b in boundaries:
    #     df_bl = df_cell[df_cell['isam'] == b[0]]
    #     df_br = df_cell[df_cell['isam'] == b[1]]
    #
    #     points.append(df_br['r0'] - )
    #
    #
    # embed()



def process_file(file):
    name = file.__class__.__name__
    input_path = get_data("d190104_vped_pedestal_steps/cell_info/{}.h5".format(name))
    output_dir = get_plot("d190104_vped_pedestal_steps/steps_vs_vped/{}".format(name))
    coi = 12

    process(input_path, output_dir, coi)


def main():
    files = [
        DC_TF_ExtSync_23deg(),
    ]
    [process_file(f) for f in files]


if __name__ == '__main__':
    main()