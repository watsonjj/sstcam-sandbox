from CHECLabPy.plotting.setup import Plotter
from CHECLabPy.plotting.camera import CameraImage
from CHECLabPy.core.io import DL1Reader
from CHECLabPy.utils.mapping import get_ctapipe_camera_geometry
from CHECOnsky.calib import obtain_cleaning_mask
from ctapipe.image.hillas import HillasParameterizationError, \
    hillas_parameters, camera_to_shower_coordinates
import argparse
from argparse import ArgumentDefaultsHelpFormatter as Formatter
import numpy as np
from numpy.polynomial.polynomial import polyfit, polyval
from tqdm import tqdm
from matplotlib import pyplot as plt
from matplotlib.patches import Ellipse
from os.path import join


class EventPlotter(Plotter):
    def __init__(self, mapping, geom):
        super().__init__()

        self.fig = plt.figure(figsize=(20, 6))
        self.ax_c = self.fig.add_subplot(1, 3, 1)
        self.ax_t = self.fig.add_subplot(1, 3, 2)
        self.ax_tg = self.fig.add_subplot(1, 3, 3)
        self.ax_tg.set_xlabel("Longtudinal distance from CoG along axis (degrees)")
        self.ax_tg.set_ylabel("Pulse time (ns)")
        self.l_tg, = self.ax_tg.plot([0], [0])
        self.p_tg, = self.ax_tg.plot([0], [0], '.')
        self.ci_c = self.create_image(
            mapping, ax=self.ax_c, clabel="Amplitude (photons)"
        )
        self.ci_t = self.create_image(
            mapping, ax=self.ax_t, clabel="Time (ns)"
        )
        self.highlights = None
        self.ellipsis = None
        self.geom = geom

    @staticmethod
    def create_image(mapping, ax, clabel):
        ci = CameraImage.from_mapping(mapping, ax=ax)
        ci.add_colorbar(clabel, pad=0)
        ci.pixels.set_linewidth(0.2)
        ci.pixels.set_edgecolor('black')
        return ci

    def set_image(self, iev, image_c, image_t, mask=None, hillas=None):
        self.ci_c.image = image_c
        self.ci_t.image = image_t
        if mask is not None:
            self.ci_t.image = np.ma.masked_array(image_t, mask=~mask)
            self.update_mask(mask)
        if hillas is not None:
            self.update_hillas(hillas)
            self.update_timing(image_c, image_t, mask, hillas)

        self.fig.suptitle(f"Event: {iev}")

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

    def update_timing(self, image_c, image_t, mask, hillas):
        image_c = image_c[mask]
        image_t = image_t[mask]
        geom = self.geom[mask]

        greater_than_0 = image_c > 0
        pix_x = geom.pix_x[greater_than_0]
        pix_y = geom.pix_y[greater_than_0]
        image = image_c[greater_than_0]
        pulse_time = image_t[greater_than_0]

        longi, trans = camera_to_shower_coordinates(
            pix_x,
            pix_y,
            hillas.x,
            hillas.y,
            hillas.psi
        )
        longi = longi.value

        self.p_tg.set_xdata(longi)
        self.p_tg.set_ydata(pulse_time)

        c = polyfit(longi, pulse_time, 1, w=np.sqrt(image))
        x = np.linspace(longi.min(), longi.max(), 10)
        y = polyval(x, c)
        self.l_tg.set_xdata(x)
        self.l_tg.set_ydata(y)
        self.ax_tg.set_title(f"tgrad = {c[1]:.2f}, psi = {hillas.psi.to('deg'):.2f}")
        self.ax_tg.relim()
        self.ax_tg.autoscale_view()


def main():
    description = 'Plot DL1 images'
    parser = argparse.ArgumentParser(description=description,
                                     formatter_class=Formatter)
    parser.add_argument('-f', '--file', dest='input_path', required=True,
                        help='path to the HDF5 dl1 file')
    parser.add_argument('-o', '--output', dest='output_dir',
                        help='directory to save the plots')
    parser.add_argument('-s', dest='start_event',
                        help='Start event', type=int)
    parser.add_argument('-m', dest='max_events',
                        help='Max events', type=int)
    args = parser.parse_args()

    input_path = args.input_path
    output = args.output_dir
    start_event = args.start_event
    max_events = args.max_events
    plot_mask = True
    plot_hillas = True

    if output is None:
        output = input_path.replace("_dl1.h5", "_dl1images")

    if start_event is None:
        start_event = 0

    with DL1Reader(input_path) as reader:
        n_events = reader.get_metadata()['n_events']
        mapping = reader.get_mapping()
        geom = get_ctapipe_camera_geometry(mapping)
        if max_events and max_events < n_events:
            n_events = max_events

        p_event = EventPlotter(mapping, geom)
        desc = "Looping over events"
        events = range(start_event, n_events)
        it = enumerate(reader.iterate_over_selected_events(events))
        for ientry, df in tqdm(it, total=n_events-start_event, desc=desc):
            iev = df['iev'].values[0]
            if iev < start_event:
                continue
            if iev >= n_events:
                break

            image_c = df['photons'].values
            image_t = df['pulse_time'].values

            mask = obtain_cleaning_mask(geom, image_c, image_t)
            if not mask.any():
                continue

            try:
                hillas = hillas_parameters(geom[mask], image_c[mask])
            except HillasParameterizationError:
                continue

            p_event.set_image(
                iev, image_c, image_t, mask=mask, hillas=hillas
            )

            p_event.save(join(output, f"{iev}.png"))


if __name__ == '__main__':
    main()
