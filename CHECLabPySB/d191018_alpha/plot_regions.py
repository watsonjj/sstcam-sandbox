from CHECLabPySB import get_astri_2019, get_plot
from CHECLabPy.core.io import HDF5Reader
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.collections import PatchCollection
from matplotlib.patches import Rectangle, Ellipse
from CHECLabPy.plotting.setup import Plotter
from CHECLabPy.utils.mapping import get_clp_mapping_from_version
from IPython import embed


class ImagePlotter(Plotter):

    def __init__(self, mapping):
        super().__init__()

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
            patches, linewidth=0.3, alpha=0.5,
            facecolor='none', edgecolor='black'
        )
        self.ax.add_collection(pixels)

        self.ax.axis('off')
        self.ax.set_aspect('equal', 'box')
        self.fig.subplots_adjust(
            left=0, right=0.95, top=0.95, bottom=0, wspace=0, hspace=0
        )
        self.ellipse = None
        self.line = None
        self.positions = {}

    def update_hillas(self, x, y, length, width, psi):
        if self.ellipse is None:
            self.ellipse = Ellipse(
                xy=(0, 0), width=0.001, height=0.001,
                angle=np.degrees(1), fill=False, color='red'
            )
            self.ax.add_patch(self.ellipse)
        self.ellipse.set_center((x, y))
        self.ellipse.width = length
        self.ellipse.height = width
        self.ellipse.angle = np.rad2deg(psi)

    def update_position(self, angle, x, y):
        if angle not in self.positions:
            if angle == 0:
                color = 'green'
            else:
                color = 'red'
            self.positions[angle], = self.ax.plot([0], [0], 'x', color=color)
        self.positions[angle].set_xdata([x])
        self.positions[angle].set_ydata([y])

    def update_line(self, cog_x, cog_y, psi):
        if self.line is None:
            self.line, = self.ax.plot(
                [0, 0], [0, 0], ls="--", c=".3"
            )
        y_min, y_max = self.ax.get_ylim()
        x_min = cog_x - (cog_y - y_min) / np.tan(psi)
        x_max = cog_x - (cog_y - y_max) / np.tan(psi)
        self.line.set_xdata([x_min, x_max])
        self.line.set_ydata([y_min, y_max])


def main():
    path = get_astri_2019("d2019-05-15_simulations/gamma_1deg.h5")
    # path = get_astri_2019("d2019-05-15_simulations/proton.h5")

    with HDF5Reader(path) as reader:
        df_hillas = reader.read('data')
        df_alpha = reader.read('alpha')
        df = pd.concat([df_hillas, df_alpha], axis=1)
        angles = reader.get_metadata('alpha')['angles']

    p_image = ImagePlotter(get_clp_mapping_from_version("1.1.0"))

    for _, row in df.iterrows():
        p_image.update_hillas(
            row['x'], row['y'], row['length'], row['width'], row['psi']
        )
        p_image.update_line(
            row['x'], row['y'], row['psi']
        )
        for angle in angles:
            p_image.update_position(
                angle, row[f'x_{angle}'], row[f'y_{angle}']
            )

        plt.pause(0.1)
    #
    # iinv = df_on['iinv'].values
    # t_cpu = df_on['t_cpu'].values
    # seperation = df_on['seperation'].values
    #
    # p_hist_sep = Hist()
    # p_hist_sep.plot(seperation[seperation<10])
    # p_hist_sep.save(get_plot("d190918_alpha/off_regions/hist_seperation.pdf"))
    #
    # p_sep_vs_time = Plotter()
    # p_sep_vs_time.ax.plot(iinv, seperation, '.')
    # p_sep_vs_time.save(get_plot("d190918_alpha/off_regions/sep_vs_time.pdf"))
    #
    #
    # # p_xy = XYPlotter(get_clp_mapping_from_version("1.1.0"))
    # # p_xy.ax.plot(df['source_x'], df['source_y'], '.', ms=1)
    # # p_xy.ax.plot(0, 0, '.', ms=1)
    # # p_xy.ax.plot(x_off, y_off, '.', ms=1)
    #
    # # files = glob("/Users/Jason/Downloads/tempdata/alpha/data/Run*_hillas.h5")
    # # for file in files:
    # #     with HDF5Reader(file) as reader:
    # #         df_hillas = reader.read('data')
    # #         df_source = reader.read('source')
    # #         df_pointing = reader.read('pointing')
    # #
    # #     telescope_pointing = get_telescope_pointing(df_pointing)
    # #     engineering_frame = get_engineering_frame(telescope_pointing)
    # #
    # #     x_off, y_off = get_off_coordinate(
    # #         df_source, telescope_pointing, engineering_frame, 270 * u.deg
    # #     )

if __name__ == '__main__':
    main()
