from CHECLabPy.plotting.setup import Plotter
from CHECLabPy.plotting.camera import CameraImage
from CHECLabPy.core.io import DL1Reader
import numpy as np
from tqdm import tqdm
from matplotlib import pyplot as plt
from os.path import join


class ImagePlotter(Plotter):
    def __init__(self, mapping):
        super().__init__()

        self.fig = plt.figure(figsize=(20, 6))
        self.ax_spmax = self.fig.add_subplot(2, 2, 1)
        self.ax_spargmax = self.fig.add_subplot(2, 2, 2)
        self.ax_c = self.fig.add_subplot(2, 2, 3)
        self.ax_t = self.fig.add_subplot(2, 2, 4)

        self.ci_spmax = self.create_image(
            mapping, ax=self.ax_spmax, clabel="SP Max"
        )
        self.ci_spargmax = self.create_image(
            mapping, ax=self.ax_spargmax, clabel="SP Argmax"
        )
        self.ci_c = self.create_image(
            mapping, ax=self.ax_c, clabel="Extracted Charge (Photons)"
        )
        self.ci_t = self.create_image(
            mapping, ax=self.ax_t, clabel="Pulse Time (ns)"
        )
        self.highlights = None

    @staticmethod
    def create_image(mapping, ax, clabel):
        ci = CameraImage.from_mapping(mapping, ax=ax)
        ci.add_colorbar(clabel, pad=0)
        ci.pixels.set_linewidth(0.2)
        ci.pixels.set_edgecolor('black')
        return ci

    def set_image(self, iev, t_cpu, sp_max, sp_argmax, image_c, image_t, mask):
        self.ci_spmax.image = sp_max
        self.ci_spargmax.image = sp_argmax
        self.ci_c.image = image_c
        self.ci_t.image = image_t
        if mask is not None:
            self.update_mask(mask)
        self.fig.suptitle(f"Event: {iev}, Time: {t_cpu}")

    def update_mask(self, mask):
        if self.highlights is None:
            self.highlights = [
                self.ci_spmax.highlight_pixels(mask, color='red'),
                self.ci_spargmax.highlight_pixels(mask, color='red'),
                self.ci_c.highlight_pixels(mask, color='red'),
                self.ci_t.highlight_pixels(mask, color='red'),
            ]
        for highlight in self.highlights:
            lw_array = np.zeros_like(self.ci_c.image)
            lw_array[mask] = 0.7
            highlight.set_linewidth(lw_array)


def main():
    path = "/Users/Jason/Downloads/tempdata/muon_search/Run13312_dl1.h5"
    output_dir = path.replace("_dl1.h5", "muonsearch")
    threshold = 40
    number = 11

    with DL1Reader(path) as reader:
        n_events = reader.n_events
        p_images = ImagePlotter(reader.mapping)
        for df in tqdm(reader.iterate_over_events(), total=n_events):
            iev = df['iev'].values[0]
            t_cpu = df['t_cpu'].values[0]

            sp_max = df['sp_max'].values
            above_threshold = sp_max > threshold
            n_above = np.sum(above_threshold)
            if n_above < number:
                continue
            sp_argmax = df['sp_argmax'].values
            image = df['photons'].values
            image_t = df['pulse_time'].values

            p_images.set_image(
                iev, t_cpu, sp_max, sp_argmax, image, image_t, above_threshold
            )
            p_images.save(join(output_dir, f"e{iev}.png"))


if __name__ == '__main__':
    main()
