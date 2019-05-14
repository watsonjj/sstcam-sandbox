from CHECLabPy.plotting.setup import Plotter
from CHECLabPy.plotting.camera import CameraImage
from CHECLabPy.core.io import DL1Reader
from CHECLabPy.utils.mapping import get_superpixel_mapping
import numpy as np
from tqdm import tqdm
from matplotlib import pyplot as plt
from os.path import join


class ImagePlotter(Plotter):
    def __init__(self, mapping):
        super().__init__()

        sp_mapping = get_superpixel_mapping(mapping)

        self.fig = plt.figure(figsize=(10, 10))
        self.ax_spmax = self.fig.add_subplot(2, 2, 1)
        self.ax_spargmax = self.fig.add_subplot(2, 2, 2)
        self.ax_c = self.fig.add_subplot(2, 2, 3)
        self.ax_t = self.fig.add_subplot(2, 2, 4)

        self.ci_spmax = self.create_image(
            sp_mapping, ax=self.ax_spmax, clabel="Above Threshold"
        )
        self.ci_spargmax = self.create_image(
            sp_mapping, ax=self.ax_spargmax, clabel="SP Argmax"
        )
        self.ci_c = self.create_image(
            mapping, ax=self.ax_c, clabel="Extracted Charge (Photons)"
        )
        self.ci_t = self.create_image(
            mapping, ax=self.ax_t, clabel="Pulse Time (ns)"
        )

        self.n_pixels = mapping.index.size
        self.n_superpixels = sp_mapping.index.size
        pix_zero = np.zeros(self.n_pixels, dtype=bool)
        sp_zero = np.zeros(self.n_superpixels, dtype=bool)
        self.ci_spmax.image = sp_zero
        self.ci_spargmax.image = sp_zero
        self.ci_c.image = pix_zero
        self.ci_t.image = pix_zero
        self.highlights = dict(
            sp_max=self.ci_spmax.highlight_pixels(sp_zero, color='red'),
            sp_argmax=self.ci_spargmax.highlight_pixels(sp_zero, color='red'),
            c=self.ci_c.highlight_pixels(pix_zero, color='black', linewidth=0.05),
            t=self.ci_t.highlight_pixels(pix_zero, color='black', linewidth=0.05),
        )

    @staticmethod
    def create_image(mapping, ax, clabel):
        ci = CameraImage.from_mapping(mapping, ax=ax)
        ci.add_colorbar(clabel, pad=0)
        # ci.pixels.set_linewidth(0.2)
        # ci.pixels.set_edgecolor('black')
        return ci

    def set_image(self, iev, t_cpu, sp_max, sp_argmax, image_c, image_t, mask):
        self.ci_spmax.image = sp_max.reshape((self.n_superpixels, 4))[:, 0]
        self.ci_spargmax.image = sp_argmax.reshape((self.n_superpixels, 4))[:, 0]
        self.ci_c.image = image_c
        self.ci_t.image = image_t
        if mask is not None:
            self._update_masks(mask)
        self.fig.suptitle(f"Event: {iev}, Time: {t_cpu}")

    def _update_masks(self, mask):
        sp_mask = mask.reshape((self.n_superpixels, 4))[:, 0]
        self._update_mask('sp_max', sp_mask)
        self._update_mask('sp_argmax', sp_mask)
        self._update_mask('c', mask)
        self._update_mask('t', mask)

    def _update_mask(self, key, mask):
        lw_array = np.zeros_like(mask)
        lw_array[mask] = 0.7
        self.highlights[key].set_linewidth(lw_array)


def main():
    path = "/Users/Jason/Downloads/tempdata/muon_search/Run13312_dl1.h5"
    output_dir = path.replace("_dl1.h5", "_muonsearch")
    threshold = 60
    number = 11

    with DL1Reader(path) as reader:
        n_events = reader.n_events
        p_images = ImagePlotter(reader.mapping)
        for df in tqdm(reader.iterate_over_events(), total=n_events):
            iev = df['iev'].values[0]
            t_cpu = df['t_cpu'].values[0]

            sp_max = df['sp_max'].values
            above_threshold = sp_max > threshold
            n_sp_above = np.sum(above_threshold) // 4
            if n_sp_above < number:
                continue
            sp_argmax = df['sp_argmax'].values
            image = df['photons'].values
            image_t = df['pulse_time'].values

            p_images.set_image(
                iev, t_cpu, above_threshold, sp_argmax, image, image_t, None
            )
            p_images.save(join(output_dir, f"e{iev}.png"))


if __name__ == '__main__':
    main()
