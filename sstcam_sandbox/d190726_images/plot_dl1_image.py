from CHECLabPy.plotting.setup import Plotter
from CHECLabPy.plotting.camera import CameraImage
from CHECLabPy.core.io import DL1Reader
from CHECLabPy.utils.mapping import get_ctapipe_camera_geometry
from CHECOnsky.calib import obtain_cleaning_mask
from ctapipe.image.hillas import HillasParameterizationError, hillas_parameters
import argparse
from argparse import ArgumentDefaultsHelpFormatter as Formatter
import numpy as np
import pandas as pd
from tqdm import tqdm
from matplotlib import pyplot as plt
from matplotlib.patches import Ellipse
from os.path import join, splitext


class ImagePlotter(Plotter):
    def __init__(self, mapping):
        super().__init__()

        self.fig = plt.figure(figsize=(20, 6))
        self.ax_c = self.fig.add_subplot(1, 3, 1)
        self.ax_t = self.fig.add_subplot(1, 3, 2)
        self.ci_c = self.create_image(
            mapping, ax=self.ax_c, clabel="Amplitude (photons)"
        )
        self.ci_t = self.create_image(
            mapping, ax=self.ax_t, clabel="Time (ns)"
        )
        self.highlights = None
        self.ellipsis = None

    @staticmethod
    def create_image(mapping, ax, clabel):
        ci = CameraImage.from_mapping(mapping, ax=ax)
        ci.add_colorbar(clabel, pad=0)
        ci.pixels.set_linewidth(0.2)
        ci.pixels.set_edgecolor('black')
        return ci

    def set_image(self, iev, image_c, image_t,
                  mask=None, hillas=None):
        self.ci_c.image = image_c
        self.ci_t.image = image_t
        if mask is not None:
            image_t_m = image_t.copy()
            image_t_m[~mask] = np.nan
            self.ci_t.image = image_t_m
            # self.update_mask(mask)
        # if hillas is not None:
        #     self.update_hillas(hillas)

        # self.fig.suptitle(f"Event: {iev}")

    def update_mask(self, mask):
        if self.highlights is None:
            self.highlights = [
                self.ci_c.highlight_pixels(mask, color='red'),
                self.ci_t.highlight_pixels(mask, color='red'),
            ]
        for highlight in self.highlights:
            lw_array = np.zeros_like(self.ci_c.image)
            lw_array[mask] = 0.7
            highlight.set_linewidth(lw_array)

    @staticmethod
    def create_ellipse(ax):
        ellipse = Ellipse(
            xy=(0, 0), width=1, height=1,
            angle=np.degrees(1), fill=False, color='red'
        )
        ax.add_patch(ellipse)
        return ellipse

    def update_hillas(self, hillas):
        if self.ellipsis is None:
            self.ellipsis = [
                self.create_ellipse(self.ax_c),
                self.create_ellipse(self.ax_t),
            ]
        for ellipse in self.ellipsis:
            ellipse.set_center((hillas.x.value, hillas.y.value))
            ellipse.width = hillas.length.value
            ellipse.height = hillas.width.value
            ellipse.angle = np.degrees(hillas.psi.rad)


def main():
    description = ('Plot the images of the events in a hillas '
                   'list from generate_list_from_hillas.py')
    parser = argparse.ArgumentParser(description=description,
                                     formatter_class=Formatter)
    parser.add_argument('-f', '--file', dest='input_path', required=True,
                        help='path to a hillas list file created by '
                             'generate_list_from_hillas')
    parser.add_argument('-n', '--max_events', dest='max_events', type=int,
                        help='number of events to plot')
    args = parser.parse_args()

    input_path = args.input_path
    output = splitext(input_path)[0]
    max_events = args.max_events

    df = pd.read_csv(input_path, sep='\t')

    # Open all files
    hillas_paths = set()
    for _, row in df.iterrows():
        hillas_paths.add(row['path'])
    readers = {path: DL1Reader(path.replace("_hillas.h5", "_dl1.h5"))
               for path in hillas_paths}

    mapping = readers[list(hillas_paths)[0]].mapping
    # mapping.metadata['size'] *= 1.01
    geom = get_ctapipe_camera_geometry(mapping)
    p_image = ImagePlotter(mapping)

    n_events = df.index.size
    if max_events is not None and n_events > max_events:
        n_events = max_events

    desc = "Looping over events"
    for i, row in tqdm(df.iterrows(), total=n_events, desc=desc):
        if i >= n_events:
            break

        hillas_path = row['path']
        iev = row['iev']
        iobs = row['iobs']
        reader = readers[hillas_path]

        df = reader[iev]
        image_c = df['photons'].values
        image_t = df['pulse_time'].values

        mask = obtain_cleaning_mask(geom, image_c, image_t)
        if not mask.any():
            continue

        try:
            hillas = hillas_parameters(geom[mask], image_c[mask])
        except HillasParameterizationError:
            continue

        p_image.set_image(
            iev, image_c, image_t, mask=mask, hillas=hillas
        )

        p_image.save(join(output, f"camera_images/i{i}_r{iobs}_e{iev}.pdf"))


if __name__ == '__main__':
    main()
