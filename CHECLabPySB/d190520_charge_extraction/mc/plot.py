from CHECLabPy.plotting.setup import Plotter
from CHECLabPy.core.io import HDF5Reader, HDF5Writer
from CHECLabPySB import get_data, get_plot
from CHECLabPy.calib.pixel_masks import PixelMasks
from os.path import dirname, abspath, join
import numpy as np
from numpy.polynomial.polynomial import polyfit
import pandas as pd
from matplotlib.ticker import FuncFormatter
from IPython import embed


DIR = abspath(dirname(__file__))


class MeanPlotter(Plotter):
    def __init__(self):
        super().__init__()
        self.style = self.next_style()

    def plot(self, extractor, df):
        df_extractor = df.loc[df['extractor'] == extractor]
        true = df_extractor['true'].values
        mean = df_extractor['mean'].values
        std = df_extractor['std'].values

        mask = true < 20
        true = true[mask]
        mean = mean[mask]
        std = std[mask]

        style = next(self.style)

        (_, caps, _) = self.ax.errorbar(
            true, mean, yerr=std, label=extractor, **style
        )
        for cap in caps:
            cap.set_markeredgewidth(0.7)

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

    def finish(self):
        self.add_legend("best")
        # self.ax.set_xscale('log')
        # self.ax.get_xaxis().set_major_formatter(
        #     FuncFormatter(lambda x, _: '{:g}'.format(x)))


class RMSEPlotter(Plotter):
    def __init__(self):
        super().__init__()
        self.style = self.next_style()

    def plot(self, extractor, df):
        df_extractor = df.loc[df['extractor'] == extractor]
        true = df_extractor['true'].values
        rmse = df_extractor['rmse'].values

        # mask = (true > 0) & (true < 100)
        mask = true < 80
        true = true[mask]
        rmse = rmse[mask]

        # res /= true

        style = next(self.style)

        self.ax.plot(true, rmse, label=extractor, **style)

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

    def finish(self):
        self.add_legend("best")
        # self.ax.set_xscale('log')
        # self.ax.get_xaxis().set_major_formatter(
        #     FuncFormatter(lambda x, _: '{:g}'.format(x)))
        self.ax.set_xlabel("True Charge (p.e)")
        self.ax.set_ylabel("RMSE")


class RMSEdivPlotter(Plotter):
    def __init__(self):
        super().__init__()
        self.style = self.next_style()

    def plot(self, extractor, df, extractor_div):
        df_extractor = df.loc[df['extractor'] == extractor]
        true = df_extractor['true'].values
        rmse = df_extractor['rmse'].values

        df_extractor = df.loc[df['extractor'] == extractor_div]
        rmse /= df_extractor['rmse'].values

        # mask = (true > 0) & (true < 100)
        mask = true < 80
        true = true[mask]
        rmse = rmse[mask]

        # res /= true

        style = next(self.style)

        self.ax.plot(true, rmse, label=extractor, **style)

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

    def finish(self):
        self.add_legend("best")
        # self.ax.set_xscale('log')
        # self.ax.get_xaxis().set_major_formatter(
        #     FuncFormatter(lambda x, _: '{:g}'.format(x)))
        self.ax.set_xlabel("True Charge (p.e)")
        self.ax.set_ylabel("RMSE w.r.t. nn_6_3")


class StdPlotter(Plotter):
    def __init__(self):
        super().__init__()
        self.style = self.next_style()

    def plot(self, extractor, df):
        df_extractor = df.loc[df['extractor'] == extractor]
        true = df_extractor['true'].values
        std = df_extractor['std'].values

        mask = true < 20
        true = true[mask]
        std = std[mask]

        style = next(self.style)

        self.ax.plot(true, std, label=extractor, **style)

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

    def finish(self):
        self.add_legend("best")
        # self.ax.set_xscale('log')
        # self.ax.get_xaxis().set_major_formatter(
        #     FuncFormatter(lambda x, _: '{:g}'.format(x)))
        # self.ax.set_yscale('log')
        # self.ax.get_yaxis().set_major_formatter(
        #     FuncFormatter(lambda y, _: '{:g}'.format(y)))


def mc():
    path = get_data("d190520_charge_extraction/mc/analysis.h5")
    output_dir = get_plot("d190520_charge_extraction/mc")

    with HDF5Reader(path) as reader:
        df = reader.read("data")

    # extractors = np.unique(df['extractor'].values)
    #
    # # All Mean
    # p_mean = MeanPlotter()
    # for extractor in extractors:
    #     p_mean.plot(extractor, df)
    # p_mean.save(join(output_dir, "mean_all.pdf"))
    #
    # # All Res
    # p_res = RMSEPlotter()
    # for extractor in extractors:
    #     p_res.plot(extractor, df)
    # p_res.save(join(output_dir, "rmse_all.pdf"))
    #
    # p_res = RMSEPlotter()
    # p_res.plot("cc_nn", df)
    # p_res.plot("cc_local", df)
    # p_res.save(join(output_dir, "rmse_cc.pdf"))
    #
    # p_std = StdPlotter()
    # p_std.plot("cc_nn", df)
    # p_std.plot("cc_local", df)
    # p_std.save(join(output_dir, "std_cc.pdf"))
    #
    # p_std = StdPlotter()
    # p_std.plot("local_5_2", df)
    # p_std.plot("local_8_4", df)
    # p_std.plot("local_11_5", df)
    # p_std.plot("nn_5_2", df)
    # p_std.plot("nn_8_4", df)
    # p_std.plot("nn_11_5", df)
    # p_std.save(join(output_dir, "std_peakfinding.pdf"))
    #
    # p_std = StdPlotter()
    # p_std.plot("sliding_local_5", df)
    # p_std.plot("sliding_local_8", df)
    # p_std.plot("sliding_local_11", df)
    # p_std.plot("sliding_nn_5", df)
    # p_std.plot("sliding_nn_8", df)
    # p_std.plot("sliding_nn_11", df)
    # p_std.save(join(output_dir, "std_sliding.pdf"))
    #
    # p_std = StdPlotter()
    # p_std.plot("cc_nn", df)
    # p_std.plot("cc_local", df)
    # p_std.plot("local_5_2", df)
    # p_std.plot("nn_5_2", df)
    # p_std.plot("sliding_local_5", df)
    # p_std.plot("sliding_nn_5", df)
    # p_std.save(join(output_dir, "std_final.pdf"))
    #
    # p_mean = MeanPlotter()
    # p_mean.plot("cc_nn", df)
    # p_mean.plot("cc_local", df)
    # p_mean.plot("local_5_2", df)
    # p_mean.plot("nn_5_2", df)
    # p_mean.plot("sliding_local_5", df)
    # p_mean.plot("sliding_nn_5", df)
    # p_mean.save(join(output_dir, "mean_final.pdf"))

    p_ress = RMSEPlotter()
    p_ress.plot("cc_nn", df)
    p_ress.plot("cc_local", df)
    p_ress.plot("sliding_local_4", df)
    p_ress.plot("sliding_nn_4", df)
    p_ress.plot("local_4_2", df)
    p_ress.plot("nn_4_2", df)
    p_ress.save(join(output_dir, "rmse_final.pdf"))

    p_ress = StdPlotter()
    p_ress.plot("cc_nn", df)
    p_ress.plot("nn_4_2", df)
    p_ress.plot("nn_8_4", df)
    p_ress.plot("nn_6_3", df)
    p_ress.save(join(output_dir, "std_nn.pdf"))

    p_ress = RMSEdivPlotter()
    p_ress.plot("cc_nn", df, "nn_6_3")
    p_ress.plot("nn_4_2", df, "nn_6_3")
    p_ress.plot("nn_6_3", df, "nn_6_3")
    p_ress.plot("nn_8_4", df, "nn_6_3")
    p_ress.plot("sliding_nn_4", df, "nn_6_3")
    p_ress.plot("sliding_nn_6", df, "nn_6_3")
    p_ress.plot("sliding_nn_8", df, "nn_6_3")
    p_ress.save(join(output_dir, "rmse_nn.pdf"))


def main():
    mc()


if __name__ == '__main__':
    main()
