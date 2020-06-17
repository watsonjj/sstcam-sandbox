from ThesisAnalysis import get_data, ThesisHDF5Reader
from sstcam_sandbox import get_plot
from ThesisAnalysis.plotting.setup import ThesisPlotter
import os
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.ticker import MultipleLocator
from CHECLabPy.core.io import DL1Reader
from CHECLabPy.spectrum_fitters.gentile import GentileFitter
from IPython import embed


class SPEPlotter(ThesisPlotter):
    def plot(self, df):
        for _, row in df.iterrows():
            type_ = row['type']
            norm = row['norm{}'.format(row['roi'])]
            edges = row['edges']
            between = row['between']
            fitx = row['fitx']
            lambda_ = row['lambda_{}'.format(row['roi'])]
            lambda_err = row['error_lambda_{}'.format(row['roi'])]
            hist = row['hist']# / norm
            fit = row['fit'] / norm

            fit /= np.trapz(fit, fitx)

            # avg = np.average(fitx, weights=fit)
            # fitx /= avg

            # from IPython import embed
            # embed()

            avg = np.average(fitx, weights=fit)
            var = np.average((fitx - avg)**2, weights=fit)
            enf = 1 + var / avg**2
            print(type_, avg, var)




            color = next(self.ax._get_lines.prop_cycler)['color']
            # self.ax.hist(between, bins=edges, weights=hist, histtype='step',
            #              color=color, normed=True)
            self.ax.plot(fitx, fit, color=color,
                         label="{} \n"
                               "ENF = {:.3f}".format(type_, enf))

        self.add_legend()
        self.ax.set_xlabel("Charge (p.e.)")
        self.ax.set_ylabel("Probability Density")
        self.ax.xaxis.set_major_locator(MultipleLocator(1))


class SPEPlotterTable(SPEPlotter):
    def __init__(self):
        super().__init__()

        self.fig = plt.figure(figsize=self.get_figsize())
        self.ax = plt.subplot2grid((3, 2), (0, 0), rowspan=3)
        self.ax_t = plt.subplot2grid((3, 2), (0, 1), rowspan=3)

    def plot(self, df):
        super().plot(df)

        type_list = []
        coeff_list = []
        errors_list = []
        for _, row in df.iterrows():
            type_ = row['type']
            coeff = dict(
                lambda_0=row['lambda_0'],
                lambda_1=row['lambda_1'],
                lambda_2=row['lambda_2'],
                eped=row['eped'],
                eped_sigma=row['eped_sigma'],
                spe=row['spe'],
                spe_sigma=row['spe_sigma'],
                opct=row['opct'],
            )
            errors = dict(
                lambda_0=row['error_lambda_0'],
                lambda_1=row['error_lambda_1'],
                lambda_2=row['error_lambda_2'],
                eped=row['error_eped'],
                eped_sigma=row['error_eped_sigma'],
                spe=row['error_spe'],
                spe_sigma=row['error_spe_sigma'],
                opct=row['error_opct'],
            )
            type_list.append(type_)
            coeff_list.append(coeff)
            errors_list.append(errors)

        self.ax_t.axis('off')
        columns = [*type_list]
        rows = list(coeff_list[0].keys())
        cells = [['%.3g ± %.3g' % (coeff_list[0][i], errors_list[0][i]),
                  '%.3g ± %.3g' % (coeff_list[1][i], errors_list[1][i])]
                 for i in rows]
        table = self.ax_t.table(cellText=cells, rowLabels=rows,
                                colLabels=columns, loc='center')
        table.set_fontsize(10)


def process(input_path, output_path):
    with ThesisHDF5Reader(input_path) as reader:
        df = reader.read("data")

    p_spe = SPEPlotter(sidebyside=True)
    p_spe.plot(df)
    p_spe.save(output_path)

    table_path = os.path.splitext(output_path)[0] + "_table.pdf"
    p_spe_table = SPEPlotterTable()
    p_spe_table.plot(df)
    p_spe_table.save(table_path)


def main():

    input_path = get_data("enf_spectrum_comparison/checm_checs.h5")
    output_path = get_plot("d190624_icrc/enf_gain.pdf")
    process(input_path, output_path)


if __name__ == '__main__':
    main()