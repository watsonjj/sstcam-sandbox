from CHECLabPy.plotting.setup import Plotter
from CHECLabPy.plotting.camera import CameraImage
from CHECLabPy.utils.mapping import get_clp_mapping_from_version
from CHECLabPy.utils.files import sort_file_list
from sstcam_sandbox import get_plot
from CHECLabPy.core.io import HDF5Reader
from matplotlib.collections import PatchCollection
from matplotlib.patches import Rectangle
from matplotlib.pyplot import cm
from glob import glob
import numpy as np
from IPython import embed


class TPlot(Plotter):
    def __init__(self):
        super().__init__()
        self.pointing_labelled = False
        self.source_labelled = False

    def plot(self, time, value, type):
        if type == "pointing":
            color = 'red'
            label = "Telescope"
            if self.pointing_labelled:
                label = None
            else:
                self.pointing_labelled = True
        else:
            color = 'blue'
            label = "Mrk421"
            if self.source_labelled:
                label = None
            else:
                self.source_labelled = True

        self.ax.plot(time, value, color=color, label=label)


class XYPlotter(Plotter):
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


def main():
    paths = sort_file_list(
        glob("/Users/Jason/Downloads/tempdata/alpha/data/*.h5")
    )

    p_alt = TPlot()
    p_az = TPlot()
    p_ra = TPlot()
    p_dec = TPlot()

    mapping = get_clp_mapping_from_version("1.1.0")
    p_xy = XYPlotter(mapping)

    for path in paths:
        with HDF5Reader(path) as reader:
            df_pointing = reader.read('pointing')
            df_source = reader.read('source')

        iobs = df_pointing['iobs'].values[0]
        t_cpu = df_pointing['t_cpu'].values
        pointing_alt = np.rad2deg(df_pointing['altitude_raw'].values)
        pointing_az = np.rad2deg(df_pointing['azimuth_raw'].values)
        pointing_ra = df_source['pointing_ra'].values
        pointing_dec = df_source['pointing_dec'].values
        source_alt = np.rad2deg(df_source['source_alt'].values)
        source_az = np.rad2deg(df_source['source_az'].values)
        source_ra = df_source['source_ra'].values
        source_dec = df_source['source_dec'].values

        p_alt.plot(t_cpu, pointing_alt, "pointing")
        p_alt.plot(t_cpu, source_alt, "source")
        p_az.plot(t_cpu, pointing_az, "pointing")
        p_az.plot(t_cpu, source_az, "source")
        p_ra.plot(t_cpu, pointing_ra, "pointing")
        p_ra.plot(t_cpu, source_ra, "source")
        p_dec.plot(t_cpu, pointing_dec, "pointing")
        p_dec.plot(t_cpu, source_dec, "source")

        source_x = df_source['source_x'].values
        source_y = df_source['source_y'].values
        p_xy.ax.plot(source_x, source_y, '.', ms=1, label=f"Run{iobs}")

        print(iobs, source_x[0], source_y[0], source_alt[0]-pointing_alt[0], source_az[0]-pointing_az[0], source_ra[0]-pointing_ra[0], source_dec[0]-pointing_dec[0])

    p_alt.ax.set_xlabel("Time")
    p_alt.ax.set_ylabel("Alt (deg)")
    p_alt.fig.autofmt_xdate()
    p_alt.add_legend("best")
    p_az.ax.set_xlabel("Time")
    p_az.ax.set_ylabel("Az (deg)")
    p_az.fig.autofmt_xdate()
    p_az.add_legend("best")
    p_ra.ax.set_xlabel("Time")
    p_ra.ax.set_ylabel("RA (deg)")
    p_ra.fig.autofmt_xdate()
    p_ra.add_legend("best")
    p_dec.ax.set_xlabel("Time")
    p_dec.ax.set_ylabel("DEC (deg)")
    p_dec.fig.autofmt_xdate()
    p_dec.add_legend("best")

    p_alt.save(get_plot("d190717_alpha/pointing_vs_time/alt.pdf"))
    p_az.save(get_plot("d190717_alpha/pointing_vs_time/az.pdf"))
    p_ra.save(get_plot("d190717_alpha/pointing_vs_time/ra.pdf"))
    p_dec.save(get_plot("d190717_alpha/pointing_vs_time/dec.pdf"))

    p_xy.add_legend("best")
    p_xy.save(get_plot("d190717_alpha/pointing_vs_time/xy.pdf"))



if __name__ == '__main__':
    main()
