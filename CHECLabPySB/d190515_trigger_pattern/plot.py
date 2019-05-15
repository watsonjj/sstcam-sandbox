from CHECLabPy.plotting.setup import Plotter
from CHECLabPy.plotting.camera import CameraImage
from CHECLabPy.core.io import TIOReader
from CHECLabPy.utils.mapping import get_superpixel_mapping
import numpy as np
from matplotlib import pyplot as plt
from ssdaq.data.io import TriggerReader


class ImagePlotter(Plotter):
    def __init__(self, mapping):
        super().__init__()

        sp_mapping = get_superpixel_mapping(mapping)

        self.fig = plt.figure(figsize=(10, 5))
        self.ax_spmax = self.fig.add_subplot(1, 2, 1)
        self.ax_trigger = self.fig.add_subplot(1, 2, 2)

        self.ci_spmax = self.create_image(
            sp_mapping, ax=self.ax_spmax, clabel="Superpixel-WF Max"
        )
        self.ci_trigger = self.create_image(
            sp_mapping, ax=self.ax_trigger, clabel="Trigger"
        )

        self.n_superpixels = sp_mapping.index.size
        sp_zero = np.zeros(self.n_superpixels, dtype=bool)
        self.ci_spmax.image = sp_zero
        self.ci_trigger.image = sp_zero
        self.highlight = self.ci_spmax.highlight_pixels(sp_zero, color='red')

    @staticmethod
    def create_image(mapping, ax, clabel):
        ci = CameraImage.from_mapping(mapping, ax=ax)
        ci.add_colorbar(clabel, pad=0)
        # ci.pixels.set_linewidth(0.2)
        # ci.pixels.set_edgecolor('black')
        return ci

    def set_image(self, t_tack, image, software_trig, trigger):
        self.ci_spmax.image = image
        self.ci_trigger.image = trigger

        lw_array = np.zeros_like(software_trig)
        lw_array[software_trig] = 0.7
        self.highlight.set_linewidth(lw_array)

        self.fig.suptitle(f"TACK: {t_tack}")


def main():
    r1_path = "/Volumes/gct-jason/astri_onsky_archive/d2019-05-10_triggerpatterns/Run13357_r1.tio"
    trig_path = "/Volumes/gct-jason/astri_onsky_archive/d2019-05-10_triggerpatterns/Run13357_2019-05-10.2100.prt"
    threshold = 42

    r1_dict = dict()
    trigger_dict = dict()

    r1_reader = TIOReader(r1_path, skip_events=0, skip_end_events=0)
    trigger_reader = TriggerReader(trig_path)

    n_pixels = r1_reader.n_pixels
    n_superpixels = n_pixels // 4
    n_samples = r1_reader.n_samples

    for i in range(35):
        r1_wfs = r1_reader[i]
        trigger_event = trigger_reader.read()

        r1_tack = r1_reader.current_tack
        trigger_tack = trigger_event.TACK

        r1_image = r1_wfs.reshape((n_superpixels, 4, n_samples)).sum(1).max(1)
        trigger_image = np.frombuffer(trigger_event.trigg.unpack(), dtype=bool)

        r1_dict[r1_tack] = r1_image
        trigger_dict[trigger_tack] = trigger_image

    p_image = ImagePlotter(r1_reader.mapping)

    tack_list = sorted(
        list(set().union(r1_dict.keys(), trigger_dict.keys()))
    )[:-1]
    for tack in tack_list:
        r1_image = r1_dict.get(tack, np.zeros(n_superpixels))
        trigger_image = trigger_dict.get(tack, np.zeros(n_superpixels))

        software_trigger = r1_image > threshold

        p_image.set_image(tack, r1_image, software_trigger, trigger_image)
        p_image.save(f"T{tack}.png")


if __name__ == '__main__':
    main()
