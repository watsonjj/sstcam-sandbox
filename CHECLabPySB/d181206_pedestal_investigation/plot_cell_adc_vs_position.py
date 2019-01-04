from CHECLabPySB.plotting.setup import Plotter
from CHECLabPySB import get_data, get_plot, HDF5Reader
import numpy as np
from matplotlib.ticker import MultipleLocator
from target_calib import CalculateRowColumnBlockPhase, GetCellIDTCArray
from CHECLabPySB.d181206_pedestal_investigation import *
# from IPython import embed
# from matplotlib import pyplot as plt


def setup_cells(df):
    fci = df['fci'].values.astype(np.uint16)
    frow, fcolumn, fblockphase = CalculateRowColumnBlockPhase(fci)
    fblock = fcolumn * 8 + frow
    df['fblock'] = fblock
    df['fblockphase'] = fblockphase
    df['fbpisam'] = df['fblockphase'] + df['isam']

    cell = GetCellIDTCArray(fci, df['isam'].values)
    row, column, blockphase = CalculateRowColumnBlockPhase(cell)
    block = column * 8 + row
    df['cell'] = cell
    df['block'] = block
    df['blockphase'] = blockphase

    df['iblock'] = (df['isam'] + df['fblockphase']) // 32

    return df


class CellWaveform(Plotter):
    def plot(self, df, cell):
        df_cell = df.loc[df['cell'] == cell]
        df_isam = df_cell.groupby('isam').agg(
            {'r0': ['mean', 'std'], 'iblock': 'mean'}
        )
        df_block = df_cell.groupby('iblock').agg(
            {'r0': ['mean', 'std'], 'isam': ['mean', 'min', 'max']}
        )

        x = df_isam.index.values
        y = df_isam['r0']['mean'].values
        yerr = df_isam['r0']['std'].values

        xb = df_block['isam']['mean'].values
        yb = df_block['r0']['mean'].values
        yberr = df_block['r0']['std'].values

        for _, row in df_block.iterrows():
            color = self.ax._get_lines.get_next_color()
            self.ax.axvline(row['isam']['min'], color=color, ls='--', alpha=0.7)
            self.ax.axvline(row['isam']['max'], color=color, ls='--', alpha=0.7)
        self.ax.errorbar(xb, yb, yerr=yberr, color='red')
        self.ax.errorbar(x, y, yerr=yerr, color='black')

        self.ax.set_xlabel("Position in waveform")
        self.ax.set_ylabel("Amplitude (Raw ADC)")
        # self.ax.set_title("Cell = {}".format(cell))

        self.ax.xaxis.set_major_locator(MultipleLocator(16))


def process(input_path, output_path):
    with HDF5Reader(input_path) as reader:
        df = reader.read("data")

    df = setup_cells(df)
    df = df.loc[~(df['r0'] == 0)]
    cells = np.unique(df['cell'].values)[:128]

    for c in cells:
        p_cellwf = CellWaveform(switch_backend=True)
        p_cellwf.plot(df, c)
        p_cellwf.save(output_path.format(c))


def process_file(file):
    name = file.__class__.__name__
    input_path = get_data("d181206_pedestal_investigation/cell_info/{}.h5".format(name))
    output_path = get_plot("d181206_pedestal_investigation/cell_adc_vs_position/{}/{}.pdf".format(name, "{}"))
    process(input_path, output_path)


def main():
    files = [
        # Pedestal_SN0038_Erlangen_23deg_OldFW_3blocks(),
        # Pedestal_SN0038_Erlangen_AC_23deg_OldFW_3blocks(),
        # Pedestal_SN0038_Erlangen_AC_40deg_OldFW_3blocks(),
        # Pedestal_SN0038_Erlangen_23deg_NewFW_3blocks(),
        # Pedestal_SN0038_Erlangen_23deg_NewFW_waitlong_3blocks(),
        # Pedestal_SN0038_Erlangen_23deg_NewFW_4blocks(),
        # Pedestal_SN0038_Erlangen_AC_23deg_NewFW_4blocks(),
        # Pedestal_SN0038_Erlangen_30deg_NewFW_4blocks(),
        # Pedestal_SN0038_MPIK_23deg_NewFW_4blocks_500Hz(),
        # Pedestal_SN0038_MPIK_23deg_NewFW_4blocks_1000Hz(),
        # Pedestal_SN0038_MPIK_23deg_NewFW_4blocks_2000Hz(),
        # Pedestal_SN0038_MPIK_23deg_NewFW_4blocks_4000Hz(),
        # Pedestal_SN0038_MPIK_23deg_NewFW_4blocks_3000Hz_cvped(),
        # Pedestal_SN0038_MPIK_23deg_NewFW_4blocks_3500Hz_cvped(),
        # Pedestal_SN0038_MPIK_23deg_NewFW_4blocks_4000Hz_cvped(),
        Pedestal_Adrian(),
    ]
    [process_file(f) for f in files]


if __name__ == '__main__':
    main()
