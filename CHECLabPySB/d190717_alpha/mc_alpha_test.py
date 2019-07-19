from CHECLabPy.plotting.setup import Plotter
from CHECLabPy.plotting.camera import CameraImage
from CHECLabPy.utils.mapping import get_clp_mapping_from_version
from CHECLabPy.utils.files import sort_file_list
from CHECLabPySB import get_plot
from CHECLabPy.core.io import HDF5Reader
from matplotlib.collections import PatchCollection
from matplotlib.patches import Rectangle, Ellipse
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.pyplot import cm
from glob import glob
import numpy as np
from matplotlib import pyplot as plt

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
        print(xpix)

        self.ax.axis('off')
        self.ax.set_aspect('equal', 'box')
        self.ax.autoscale_view()
        self.fig.subplots_adjust(
            left=0, right=0.95, top=0.95, bottom=0, wspace=0, hspace=0
        )

        self.ellipse = Ellipse(
            xy=(0, 0), width=0.01, height=0.01,
            angle=np.degrees(1), fill=False, color='red'
        )
        self.ax.add_patch(self.ellipse)

        self.line, = self.ax.plot(
            self.ax.get_xlim(), self.ax.get_ylim(), ls="--", c=".3"
        )

        self.src, = self.ax.plot(0, 0, 'x')

    def update(self, cog_x, cog_y, length, width, psi, src_x, src_y):
        self.ellipse.set_center((cog_x, cog_y))
        self.ellipse.width = length
        self.ellipse.height = width
        self.ellipse.angle = np.degrees(psi)

        y_min, y_max = self.ax.get_ylim()
        x_min = cog_x - (cog_y - y_min) / np.tan(psi)
        x_max = cog_x - (cog_y - y_max) / np.tan(psi)
        self.line.set_xdata([x_min, x_max])
        self.line.set_ydata([y_min, y_max])

        self.src.set_xdata(src_x)
        self.src.set_ydata(src_y)






def main():
    # path = "/Users/Jason/Downloads/tempdata/alpha/mc/gamma_1deg.h5"
    path = "/Volumes/gct-jason/astri_onsky_archive/d2019-05-15_simulations/gamma_1deg/run1_hillas.h5"

    with HDF5Reader(path) as reader:
        df_hillas = reader.read("data")
        df_source = reader.read("source")
        mapping = reader.get_mapping()

    # mapping = get_clp_mapping_from_version("1.1.0")
    p_image = ImagePlotter(mapping)

    order = np.argsort(df_source['alpha90'])

    with PdfPages(get_plot("d190717_alpha/mc_alpha_test.pdf")) as pdf:
        for index in order:
            row_hillas = df_hillas.iloc[index]
            row_source = df_source.iloc[index]
            cog_x = row_hillas['x']
            cog_y = row_hillas['y']
            length = row_hillas['length']
            width = row_hillas['width']
            psi = row_hillas['psi']
            src_x = row_source['source_x']
            src_y = row_source['source_y']
            alpha90 = row_source['alpha90']

            p_image.update(cog_x, cog_y, length, width, psi, src_x, src_y)
            p_image.ax.set_title(np.rad2deg(alpha90))
            # pdf.savefig(p_image.fig)
            plt.pause(0.3)




if __name__ == '__main__':
    main()
