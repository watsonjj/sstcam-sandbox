from CHECLabPy.plotting.setup import Plotter
from CHECLabPy.plotting.camera import CameraImage
from CHECLabPy.utils.files import create_directory
from CHECLabPy.utils.mapping import get_ctapipe_camera_geometry
from CHECLabPySB import get_plot, get_data
from os.path import join
from matplotlib import pyplot as plt
from tqdm import tqdm
import numpy as np
import pandas as pd
import warnings
from CHECOnsky.calib import obtain_cleaning_mask
from CHECLabPy.calib import TimeCalibrator
from mpl_toolkits.axes_grid1 import make_axes_locatable
from IPython import embed


def colorbar(mappable, label):
    ax = mappable.axes
    fig = ax.figure
    divider = make_axes_locatable(ax)
    _ = divider.append_axes("right", size="10%", pad=0.15)
    cax = divider.append_axes("right", size="10%", pad=0.15)
    return fig.colorbar(mappable, label=label, cax=cax, aspect=20)


class CameraMovie(Plotter):
    def __init__(self, mapping, output_path):
        super().__init__()

        self.fig = plt.figure(figsize=(8, 3))
        self.ax_goldfish = self.fig.add_axes([0, 0, 0.4, 1])
        self.ax_image = self.fig.add_axes([0.4, 0, 0.4, 1])
        self.ax_cb = self.fig.add_axes([0.68, 0, 0.15, 1])
        self.ax_image.patch.set_alpha(0)
        self.ax_cb.patch.set_alpha(0)
        self.ax_cb.axis('off')
        self.ci_image = CameraImage.from_mapping(mapping, ax=self.ax_image)
        self.ci_image.add_colorbar(
            "Pixel Amplitude (p.e.)", ax=self.ax_cb, pad=-0.5
        )
        self.ci_goldfish = CameraImage.from_mapping(mapping, ax=self.ax_goldfish)

        self.output_path = output_path
        self.source_point_image = None
        self.source_point_goldfish = None
        self.source_label_image = None
        self.source_label_goldfish = None
        self.alpha_line = None
        self.timestamp = None
        self.iframe = 0

    def set_source_position(self, x_src, y_src):
        offset = 0.004
        if self.source_point_image is None:
            self.source_point_image, = self.ax_image.plot(
                x_src, y_src, 'x', c='red'
            )
            self.source_label_image = self.ax_image.text(
                x_src+offset, y_src+offset, "Mrk421", color='red', size=10
            )
        else:
            self.source_point_image.set_xdata(x_src)
            self.source_point_image.set_ydata(y_src)
            self.source_label_image.set_position((x_src+offset, y_src+offset))

        if self.source_point_goldfish is None:
            self.source_point_goldfish, = self.ax_goldfish.plot(
                x_src, y_src, 'x', c='red'
            )
            self.source_label_goldfish = self.ax_goldfish.text(
                x_src+offset, y_src+offset, "Mrk421", color='red', size=10
            )
        else:
            self.source_point_goldfish.set_xdata(x_src)
            self.source_point_goldfish.set_ydata(y_src)
            self.source_label_goldfish.set_position((x_src+offset, y_src+offset))

    def set_timestamp(self, timestamp):
        timestamp_str = str(timestamp)
        timestamp_len = len(timestamp_str)
        missing = 29 - timestamp_len
        timestamp_str += "0" * missing
        if self.timestamp is None:
            self.timestamp = self.fig.text(
                0.4, -0.1, timestamp_str, horizontalalignment='center', size=12
            )
        else:
            self.timestamp.set_text(timestamp_str)

    def set_image(self, image, min_=None, max_=None):
        self.ci_image.image = image
        self.ci_image.set_limits_minmax(min_, max_)

    def set_goldfish(self, slice, min_=None, max_=None):
        self.ci_goldfish.image = slice
        self.ci_goldfish.set_limits_minmax(min_, max_)

    def set_alpha_line(self, cog_x, cog_y, psi):
        y_min, y_max = self.ax_image.get_ylim()
        x_min = cog_x - (cog_y - y_min) / np.tan(psi)
        x_max = cog_x - (cog_y - y_max) / np.tan(psi)
        if self.alpha_line is None:
            self.alpha_line, = self.ax_image.plot(
                [x_min, x_max], [y_min, y_max], ls="--", c='red'
            )
        else:
            self.alpha_line.set_xdata([x_min, x_max])
            self.alpha_line.set_ydata([y_min, y_max])

    def save_frame(self):
        path = self.output_path.format(self.iframe)
        self.fig.savefig(path, bbox_inches='tight')
        self.iframe += 1


def main():
    path = get_data("d190717_alpha/wobble.h5")
    with pd.HDFStore(path, mode='r') as store:
        df = store['data'].loc[::4]
        mapping = store['mapping']
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', UserWarning)
            mapping.metadata = store.get_storer('mapping').attrs.metadata

    tc = TimeCalibrator()
    geom = get_ctapipe_camera_geometry(mapping)

    n_row = df.index.size
    p_camera = CameraMovie(mapping, get_plot(
        "d190717_alpha/wobble_animation_goldfish/frames/{:04d}.png"
    ))
    for _, row in tqdm(df.iterrows(), total=n_row):
        timestamp = row['timestamp']
        iobs = row['iobs']
        iev = row['iev']
        x_src = row['x_src']
        y_src = row['y_src']
        dl1 = row['dl1'].values
        time = row['dl1_pulse_time'].values
        r1 = row['r1']
        x_cog = row['x_cog']
        y_cog = row['y_cog']
        psi = row['psi']
        p_camera.set_source_position(x_src, y_src)


        n_pixels, n_samples = r1.shape
        shifted = tc(r1)

        mask = obtain_cleaning_mask(geom, dl1, time)
        if not mask.any():
            msg = f"No pixels survived cleaning for: RUN {iobs} IEV {iev}"
            print(msg)
            continue
            # raise ValueError(msg)

        dl1_ma = np.ma.masked_array(dl1, mask=~mask)

        min_pixel = dl1_ma.argmin()
        max_pixel = dl1_ma.argmax()

        min_image = -4
        max_image = 0.7 * dl1.max()

        min_gf = shifted[max_pixel, :20].min()
        max_gf = shifted[max_pixel].max() * 0.8

        st = int(np.min(time[mask]) - 3)
        et = int(np.max(time[mask]) + 6)
        st = st if st > 0 else 0
        et = et if et < n_samples else n_samples

        # embed()
        p_camera.set_image(dl1, min_image, max_image)

        for t in range(st, et, 3):
            slice_ = shifted[:, t]
            p_camera.set_timestamp(timestamp + pd.Timedelta(f"{t}ns"))
            p_camera.set_goldfish(slice_, min_gf, max_gf)
            p_camera.save_frame()


if __name__ == '__main__':
    main()
