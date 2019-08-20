from CHECLabPy.plotting.setup import Plotter
from CHECLabPySB import get_data, get_plot
from CHECLabPySB.d190730_pedestal import setup_cells, all_files
from CHECLabPy.core.io import HDF5Reader
import numpy as np
from matplotlib.ticker import MultipleLocator
from os.path import join
from IPython import embed


class CellWaveform(Plotter):
    def plot(self, df, cell):
        df_cell = df.loc[df['cell'] == cell]
        df_isam = df_cell.groupby('isam').agg(
            {'adc': ['mean', 'std'], 'iblock': 'mean'}
        )
        df_block = df_cell.groupby('iblock').agg(
            {'adc': ['mean', 'std'], 'isam': ['mean', 'min', 'max']}
        )

        x = df_isam.index.values
        y = df_isam['adc']['mean'].values
        yerr = df_isam['adc']['std'].values

        xb = df_block['isam']['mean'].values
        yb = df_block['adc']['mean'].values
        yberr = df_block['adc']['std'].values

        for _, row in df_block.iterrows():
            color = self.ax._get_lines.get_next_color()
            self.ax.axvline(row['isam']['min'], color=color, ls='--', alpha=0.7)
            self.ax.axvline(row['isam']['max'], color=color, ls='--', alpha=0.7)
        self.ax.errorbar(xb, yb, yerr=yberr, color='red')
        self.ax.errorbar(x, y, yerr=yerr, color='black')

        self.ax.set_xlabel("Position in waveform")
        self.ax.set_ylabel("Amplitude (Raw ADC)")
        self.ax.set_title("Cell = {}".format(cell))

        self.ax.xaxis.set_major_locator(MultipleLocator(16))


def process_all_cells(input_path, output_path):
    with HDF5Reader(input_path) as reader:
        df = reader.read("data")

    df = setup_cells(df)
    cells = np.unique(df['cell'].values)[:128]

    for c in cells:
        p_cellwf = CellWaveform()
        p_cellwf.plot(df, c)
        p_cellwf.save(output_path.format(c))


def process_one_cell(input_path, output_path, cell):
    with HDF5Reader(input_path) as reader:
        df = reader.read("data")

    df = setup_cells(df)

    p_cellwf = CellWaveform()
    p_cellwf.plot(df, cell)
    p_cellwf.save(output_path.format(cell))


def main():
    for file in all_files:
        output = join(file.plot_dir, "cell_adc_vs_position_c{}.pdf")
        process_one_cell(file.reduced_cell_info, output, 25)

    for file in all_files:
        output = join(file.plot_dir, "cell_adc_vs_position/{}.pdf")
        process_all_cells(file.reduced_cell_info, output)


if __name__ == '__main__':
    main()
