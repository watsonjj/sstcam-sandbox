from CHECLabPy.plotting.setup import Plotter
from CHECLabPy.plotting.camera import CameraImage
from CHECLabPy.utils.files import create_directory
from sstcam_sandbox import get_plot, get_data
from os.path import join
from matplotlib import pyplot as plt
from tqdm import tqdm
import numpy as np
import pandas as pd
import warnings
from IPython import embed


class CameraMovie(Plotter):
    def __init__(self, mapping, output_dir):
        super().__init__()

        self.fig = plt.figure(figsize=(8, 6))
        self.ax = self.fig.add_subplot(1, 1, 1)

        self.ci = CameraImage.from_mapping(mapping, ax=self.ax)
        self.ci.add_colorbar("Pixel Amplitude (p.e.)", pad=-0.15)
        # self.ci.colorbar.set_label("Pixel Amplitude (p.e.)", labelpad=20)
        self.output_dir = output_dir
        self.source_point = None
        self.source_label = None
        self.alpha_line = None
        self.iframe = 0

        create_directory(output_dir)

    def set_source_position(self, x_src, y_src):
        if self.source_point is None:
            self.source_point, = self.ci.ax.plot(x_src, y_src, 'x', c='red')
            self.source_label = self.ci.ax.text(
                x_src+0.004, y_src+0.004, "Mrk421", color='red', size=10
            )
        else:
            self.source_point.set_xdata(x_src)
            self.source_point.set_ydata(y_src)
            self.source_label.set_position((x_src+0.004, y_src+0.004))

    def set_image(self, image, min_=None, max_=None):
        self.ci.image = image
        self.ci.set_limits_minmax(min_, max_)

    def set_alpha_line(self, cog_x, cog_y, psi):
        y_min, y_max = self.ax.get_ylim()
        x_min = cog_x - (cog_y - y_min) / np.tan(psi)
        x_max = cog_x - (cog_y - y_max) / np.tan(psi)
        if self.alpha_line is None:
            self.alpha_line, = self.ax.plot(
                [x_min, x_max], [y_min, y_max], ls="--", c='red'
            )
        else:
            self.alpha_line.set_xdata([x_min, x_max])
            self.alpha_line.set_ydata([y_min, y_max])

    def save_frame(self):
        path = join(self.output_dir, f"{self.iframe}.png")
        # self.fig.tight_layout(pad=2)
        self.fig.savefig(path)#, bbox_inches='tight')
        self.iframe += 1


def main():
    path = get_data("d190717_alpha/wobble.h5")
    with pd.HDFStore(path, mode='r') as store:
        df = store['data']
        mapping = store['mapping']
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', UserWarning)
            mapping.metadata = store.get_storer('mapping').attrs.metadata

    p_camera = CameraMovie(mapping, get_plot(
        "d190717_alpha/wobble_animation/frames"
    ))
    n_row = df.index.size
    for _, row in tqdm(df.iterrows(), total=n_row):
        timestamp = row['timestamp']
        x_src = row['x_src']
        y_src = row['y_src']
        dl1 = row['dl1']
        r1 = row['r1']
        x_cog = row['x_cog']
        y_cog = row['y_cog']
        psi = row['psi']
        p_camera.set_source_position(x_src, y_src)
        p_camera.set_image(dl1)
        # p_camera.set_alpha_line(x_cog, y_cog, psi)
        p_camera.save_frame()


if __name__ == '__main__':
    main()
