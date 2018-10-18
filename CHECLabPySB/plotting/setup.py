import matplotlib as mpl
ORIGINAL_BACKEND = mpl.get_backend()
mpl.use('pgf')
from matplotlib import pyplot as plt
import os
import numpy as np
from CHECLabPy.utils.files import create_directory


class Plotter:
    def __init__(self, ax=None, sidebyside=False, switch_backend=False):
        self.sidebyside = sidebyside

        self.switch_backend = switch_backend
        if self.switch_backend:
            plt.switch_backend(ORIGINAL_BACKEND)

        rc = {  # setup matplotlib to use latex for output
            "pgf.texsystem": "pdflatex", # change this if using xetex or lautex
            "text.usetex": True,         # use LaTeX to write all text
            "font.family": 'lmodern',
            # "font.family": "cursive",
            "font.serif": [],            # blank entries should cause plots to inherit fonts from the document
            "font.sans-serif": [],
            "font.monospace": [],
            "font.cursive": [],
            "font.size": 10,
            "axes.titlesize": 10,
            "axes.labelsize": 10,        # LaTeX default is 10pt font.
            "legend.fontsize": 8,        # Make the legend/label fonts a little smaller
            "axes.prop_cycle": plt.cycler(color=plt.cm.Dark2.colors),

            # Set x axis
            "xtick.labelsize": 8,
            "xtick.direction": 'in',
            "xtick.major.size": 3,
            "xtick.major.width": 0.5,
            "xtick.minor.size": 1.5,
            "xtick.minor.width": 0.5,
            "xtick.minor.visible": True,
            "xtick.top": True,

            # Set y axis
            "ytick.labelsize": 8,
            "ytick.direction": 'in',
            "ytick.major.size": 3,
            "ytick.major.width": 0.5,
            "ytick.minor.size": 1.5,
            "ytick.minor.width": 0.5,
            "ytick.minor.visible": True,
            "ytick.right": True,

            "axes.linewidth": 0.5,
            "grid.linewidth": 0.5,
            "lines.linewidth": 1.,

            "savefig.bbox": 'tight',
            "savefig.pad_inches": 0.05,

            "figure.figsize": self.get_figsize(),
            "lines.markeredgewidth": 1,
            "pgf.preamble": [
                r"\usepackage[utf8x]{inputenc}", # use utf8 fonts becasue your computer can handle it :)
                r"\usepackage[T1]{fontenc}", # plots will be generated using this preamble
                r"\usepackage{amsmath}",
                r"\usepackage{pgfplots}",
                r"\usepackage{gensymb}",
                r"\usepackage{siunitx}",
                r"\DeclareSIUnit{\pe}{{p.e.}}",
                r"\newcommand*\average[1]{\bar{#1}}"
            ]
        }

        mpl.rcParams.update(rc)

        if ax:
            self.ax = ax
            self.fig = ax.figure
        else:
            self.fig, self.ax = self.create_figure()

    @staticmethod
    def golden_figsize(scale=0.9):
        fig_width_pt = 421.10046  # Get this from LaTeX using \the\textwidth
        inches_per_pt = 1.0 / 72.27  # Convert pt to inch
        golden_mean = (np.sqrt(5.0) - 1.0) / 2.0  # Aesthetic ratio
        fig_width = fig_width_pt * inches_per_pt * scale  # width in inches
        fig_height = fig_width * golden_mean  # height in inches
        fig_size = [fig_width, fig_height]
        return fig_size

    def get_figsize(self):
        if self.sidebyside:
            return self.golden_figsize(0.6)
        else:
            return self.golden_figsize(0.9)

    def create_figure(self):
        fig = plt.figure(figsize=self.get_figsize())
        ax = fig.add_subplot(1, 1, 1)

        # fmt = mpl.ticker.StrMethodFormatter("{x}")
        # ax.xaxis.set_major_formatter(fmt)
        # ax.yaxis.set_major_formatter(fmt)
        return fig, ax

    def add_legend(self, loc="upper right", **kwargs):
        self.ax.legend(loc=loc, **kwargs)

    @staticmethod
    def create_directory(directory):
        create_directory(directory)

    def finish(self):
        pass

    def save(self, output_path):
        self.finish()
        output_dir = os.path.dirname(output_path)
        self.create_directory(output_dir)
        # self.fig.tight_layout()
        self.fig.savefig(output_path, bbox_inches='tight')
        print("Figure saved to: {}".format(output_path))

        if self.switch_backend:
            plt.switch_backend('pgf')

        plt.close(self.fig)
