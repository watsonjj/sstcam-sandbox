from CHECLabPy.plotting.setup import Plotter
from CHECLabPy.core.io import HDF5Reader
from CHECLabPySB import get_data, get_plot
from os.path import join
import numpy as np
from matplotlib.ticker import FuncFormatter
from matplotlib.colors import LogNorm
from matplotlib.collections import PatchCollection
from matplotlib.patches import Rectangle, Circle
from matplotlib.pyplot import cm
import seaborn as sns
from scipy.stats import kde
from IPython import embed



class COGPlotter(Plotter):
    def plot(self, x, y, mapping):

        cmap = cm.viridis
        sns.kdeplot(
            x, y, ax=self.ax, shade=True, n_levels=100,
            cmap=cmap, shade_lowest=False, cbar=True
        )

        xpix = mapping['xpix'].values
        ypix = mapping['ypix'].values
        size = mapping.metadata['size']

        patches = []
        for xx, yy in zip(xpix, ypix):
            rr = size + 0.0001  # extra size to pixels to avoid aliasing
            poly = Rectangle(
                (xx - rr / 2., yy - rr / 2.),
                width=rr,
                height=rr,
                fill=True,
            )
            patches.append(poly)
        pixels = PatchCollection(
            patches, linewidth=0.3, alpha=1,
            facecolor='none', edgecolor='white'
        )
        self.ax.add_collection(pixels)

        self.ax.set_xlabel("X position (m)")
        self.ax.set_ylabel("Y position (m)")
        self.ax.axis('off')
        self.ax.set_aspect('equal', 'box')
        self.fig.subplots_adjust(
            left=0, right=0.95, top=0.95, bottom=0, wspace=0, hspace=0
        )


def main():
    path = get_data("d190522_hillas_over_campaign/hillas.h5")
    path_mc = "/Volumes/gct-jason/astri_onsky_archive/d2019-05-15_simulations/proton.h5"

    with HDF5Reader(path) as reader:
        df = reader.read("data")
        mapping = reader.get_mapping()

        df = df.loc[(df['width'] * df['length'] / df['concentration_1']) < 20]

    with HDF5Reader(path_mc) as reader:
        df_mc = reader.read("data")
        mapping_mc = reader.get_mapping()

    output_dir = get_plot("d190522_hillas_over_campaign/cog")

    for _, group in df.groupby("iinv"):
        investigation = group.iloc[0]['investigation']
        x = group['x'].values
        y = group['y'].values

        p_cog = COGPlotter()
        p_cog.plot(x, y, mapping)
        p_cog.save(join(output_dir, f"{investigation}.png"), dpi=1000)

    x = df['x'].values
    y = df['y'].values
    p_cog = COGPlotter()
    p_cog.plot(x, y, mapping)
    p_cog.save(join(output_dir, f"all.png"), dpi=1000)

    df_week1 = df.loc[df['iinv'] < 6]
    x = df_week1['x'].values
    y = df_week1['y'].values
    p_cog = COGPlotter()
    p_cog.plot(x, y, mapping)
    p_cog.save(join(output_dir, "week1.png"), dpi=1000)

    df_week2 = df.loc[df['iinv'] >= 6]
    x = df_week2['x'].values
    y = df_week2['y'].values
    p_cog = COGPlotter()
    p_cog.plot(x, y, mapping)
    p_cog.save(join(output_dir, "week2.png"), dpi=1000)

    x = df_mc['x'].values
    y = df_mc['y'].values
    p_cog = COGPlotter()
    p_cog.plot(x, y, mapping)
    p_cog.save(join(output_dir, f"mc.png"), dpi=1000)

if __name__ == '__main__':
    main()
