from CHECLabPy.plotting.setup import Plotter
from CHECLabPy.core.io import HDF5Reader
from sstcam_sandbox import get_data, get_plot
from os.path import join
import numpy as np
from matplotlib.ticker import FuncFormatter
from IPython import embed


class HillasPlotter(Plotter):
    def __init__(self, xlabel):
        super().__init__()
        self.style = self.next_style()
        self.line_pallette = ['-', '--']

        self.ax.set_xlabel(xlabel)
        self.ax.set_ylabel("Density")

        self.edges = None
        self.between = None

    def next_style(self):
        def next_ls():
            while True:
                for i in range(8):
                    yield '-'
                for i in range(8):
                    yield '--'

        ls = next_ls()

        while True:
            yield dict(
                color=next(self.ax._get_lines.prop_cycler)['color'],
                ls=next(ls),
            )

    def add(self, values, investigation):
        style = next(self.style)

        self.ax.hist(
            values, bins='auto', density=True, **style,
            histtype='step', label=investigation
        )

    def finish(self):
        self.add_legend("best", fontsize=4)
        self.ax.set_yscale('log')
        # self.ax.get_yaxis().set_major_formatter(
        #     FuncFormatter(lambda y, _: '{:g}'.format(y)))


def main():
    path = get_data("d190522_hillas_over_campaign/hillas.h5")

    with HDF5Reader(path) as reader:
        df = reader.read("data")
        mapping = reader.get_mapping()

    output_dir = get_plot("d190522_hillas_over_campaign")

    p_hillas = HillasPlotter("Width (degrees)")
    for _, group in df.groupby("iinv"):
        investigation = group.iloc[0]['investigation']
        values = group['width'].values
        p_hillas.add(values, investigation)
    p_hillas.save(join(output_dir, f"width.pdf"))

    p_hillas = HillasPlotter("Length (degrees)")
    for _, group in df.groupby("iinv"):
        investigation = group.iloc[0]['investigation']
        values = group['length'].values
        p_hillas.add(values, investigation)
    p_hillas.save(join(output_dir, f"length.pdf"))

    p_hillas = HillasPlotter("Intensity (photons)")
    for _, group in df.groupby("iinv"):
        investigation = group.iloc[0]['investigation']
        values = group['intensity'].values
        p_hillas.add(values, investigation)
    p_hillas.ax.set_xscale('log')
    p_hillas.save(join(output_dir, f"intensity.pdf"))

    p_hillas = HillasPlotter("Psi (radians)")
    for _, group in df.groupby("iinv"):
        investigation = group.iloc[0]['investigation']
        values = group['psi'].values
        p_hillas.add(values, investigation)
    p_hillas.save(join(output_dir, f"psi.pdf"))

    p_hillas = HillasPlotter("Phi (radians)")
    for _, group in df.groupby("iinv"):
        investigation = group.iloc[0]['investigation']
        values = group['phi'].values
        p_hillas.add(values, investigation)
    p_hillas.save(join(output_dir, f"phi.pdf"))

    p_hillas = HillasPlotter("Skewness")
    for _, group in df.groupby("iinv"):
        investigation = group.iloc[0]['investigation']
        values = group['skewness'].values
        p_hillas.add(values, investigation)
    p_hillas.save(join(output_dir, f"skewness.pdf"))

    p_hillas = HillasPlotter("Kurtosis")
    for _, group in df.groupby("iinv"):
        investigation = group.iloc[0]['investigation']
        values = group['kurtosis'].values
        p_hillas.add(values, investigation)
    p_hillas.ax.set_xscale('log')
    p_hillas.save(join(output_dir, f"kurtosis.pdf"))

    p_hillas = HillasPlotter("Intensity/Length")
    for _, group in df.groupby("iinv"):
        investigation = group.iloc[0]['investigation']
        values = group['intensity'].values / group['length'].values
        p_hillas.add(values, investigation)
    p_hillas.ax.set_xscale('log')
    p_hillas.save(join(output_dir, f"intensity_length.pdf"))

    p_hillas = HillasPlotter("Width (degrees) (intensity < 400)")
    for _, group in df.groupby("iinv"):
        mask = group['intensity'].values < 400
        investigation = group.iloc[0]['investigation']
        values = group['width'].values[mask]
        p_hillas.add(values, investigation)
    p_hillas.save(join(output_dir, f"width_cut_i400.pdf"))

    p_hillas = HillasPlotter("Concentration1")
    for _, group in df.groupby("iinv"):
        investigation = group.iloc[0]['investigation']
        values = group['concentration_1'].values
        p_hillas.add(values, investigation)
    p_hillas.save(join(output_dir, f"concentration_1.pdf"))

    p_hillas = HillasPlotter("Concentration2")
    for _, group in df.groupby("iinv"):
        investigation = group.iloc[0]['investigation']
        values = group['concentration_2'].values
        p_hillas.add(values, investigation)
    p_hillas.save(join(output_dir, f"concentration_2.pdf"))

    p_hillas = HillasPlotter("Concentration3")
    for _, group in df.groupby("iinv"):
        investigation = group.iloc[0]['investigation']
        values = group['concentration_3'].values
        p_hillas.add(values, investigation)
    p_hillas.save(join(output_dir, f"concentration_3.pdf"))



if __name__ == '__main__':
    main()
