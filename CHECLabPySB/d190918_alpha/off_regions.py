from CHECLabPySB import get_data, get_plot
from CHECLabPy.core.io import HDF5Reader
from CHECOnsky.scripts_analysis.add_pointing_to_hillas import LOCATION, \
    FOCAL_LENGTH, EngineeringCameraFrame
from glob import glob
import numpy as np
from astropy.coordinates import SkyCoord, AltAz
from astropy import units as u
from IPython import embed
from matplotlib import pyplot as plt
from matplotlib.collections import PatchCollection
from matplotlib.patches import Rectangle
from CHECLabPy.plotting.setup import Plotter
from CHECLabPy.utils.mapping import get_clp_mapping_from_version



# def get_telescope_pointing(df_pointing):
#     obstime = df_pointing['t_cpu']
#     alt = (df_pointing['altitude_raw'] +
#            df_pointing['altitude_cor']).values
#     az = (df_pointing['azimuth_raw'] +
#           df_pointing['azimuth_cor']).values
#     altaz_frame = AltAz(location=LOCATION, obstime=obstime)
#     return SkyCoord(
#         alt=alt,
#         az=az,
#         unit='rad',
#         frame=altaz_frame,
#     )
#
#
# def get_engineering_frame(telescope_pointing):
#     return EngineeringCameraFrame(
#         n_mirrors=2,
#         location=LOCATION,
#         obstime=telescope_pointing.obstime,
#         focal_length=FOCAL_LENGTH,
#         telescope_pointing=telescope_pointing,
#     )

class Hist(Plotter):
    def plot(self, values):
        self.ax.hist(values, bins=100)


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


# def get_off_coordinate(df_source, telescope_pointing, engineering_frame, angle):
#     source_ra = df_source['source_ra']
#     source_dec = df_source['source_dec']
#
#     source_skycoord = SkyCoord(source_ra, source_dec, unit='deg', frame='icrs')
#     position_angle = telescope_pointing.position_angle(
#         source_skycoord
#     ).to(u.deg) - angle
#     seperation = telescope_pointing.separation(source_skycoord)
#     off_skycoord = telescope_pointing.directional_offset_by(
#         position_angle=position_angle,
#         separation=seperation
#     )
#
#     off_cam = off_skycoord.transform_to(engineering_frame)
#     x_off = off_cam.x.value
#     y_off = off_cam.y.value
#
#     embed()
#
#     plt.plot(source_ra, source_dec, '.')
#     plt.plot(telescope_pointing.icrs.ra, telescope_pointing.icrs.dec, '.')
#     plt.plot(off_skycoord.icrs.ra, off_skycoord.icrs.dec, '.')
#
#     ci = XYPlotter(get_clp_mapping_from_version("1.1.0"))
#     ci.ax.plot(df_source['source_x'], df_source['source_y'], '.', ms=1)
#     ci.ax.plot(0, 0, '.', ms=1)
#     ci.ax.plot(x_off, y_off, '.', ms=1)
#
#     plt.show()
#
#     return x_off, y_off


def main():
    path = get_data("d190918_alpha/onsky_wobble.h5")
    with HDF5Reader(path) as reader:
        df_on = reader.read('on')
        df_off = reader.read('off')

    iinv = df_on['iinv'].values
    t_cpu = df_on['t_cpu'].values
    seperation = df_on['seperation'].values

    p_hist_sep = Hist()
    p_hist_sep.plot(seperation[seperation<10])
    p_hist_sep.save(get_plot("d190918_alpha/off_regions/hist_seperation.pdf"))

    p_sep_vs_time = Plotter()
    p_sep_vs_time.ax.plot(iinv, seperation, '.')
    p_sep_vs_time.save(get_plot("d190918_alpha/off_regions/sep_vs_time.pdf"))


    # p_xy = XYPlotter(get_clp_mapping_from_version("1.1.0"))
    # p_xy.ax.plot(df['source_x'], df['source_y'], '.', ms=1)
    # p_xy.ax.plot(0, 0, '.', ms=1)
    # p_xy.ax.plot(x_off, y_off, '.', ms=1)

    # files = glob("/Users/Jason/Downloads/tempdata/alpha/data/Run*_hillas.h5")
    # for file in files:
    #     with HDF5Reader(file) as reader:
    #         df_hillas = reader.read('data')
    #         df_source = reader.read('source')
    #         df_pointing = reader.read('pointing')
    #
    #     telescope_pointing = get_telescope_pointing(df_pointing)
    #     engineering_frame = get_engineering_frame(telescope_pointing)
    #
    #     x_off, y_off = get_off_coordinate(
    #         df_source, telescope_pointing, engineering_frame, 270 * u.deg
    #     )

if __name__ == '__main__':
    main()
