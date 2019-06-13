from CHECLabPySB import get_astri_2019, get_plot
from CHECLabPy.core.io import TIOReader
from CHECLabPy.plotting.waveform import CameraPixelWaveformPlotter
from CHECLabPy.calib import PixelMasks, get_calib_data
from CHECOnsky.calib import get_calib_data as get_onsky_calib_data
from CHECLabPy.utils.mapping import get_superpixel_mapping
import numpy as np
import pandas as pd
from tqdm import tqdm
import matplotlib as mpl
from IPython import embed


class CameraPlotter(CameraPixelWaveformPlotter):
    def __init__(self, mapping, pixelmask):
        super().__init__(mapping)
        # self.pm = pixelmask
        # for pix in np.where(pixelmask.dead)[0]:
        #     for key, spine in self.ax_dict[pix].spines.items():
        #         spine.set_visible(True)
        #         spine.set_color('red')
        #         spine.set_linewidth(1)
        # for pix in np.where(pixelmask.low)[0]:
        #     for key, spine in self.ax_dict[pix].spines.items():
        #         spine.set_visible(True)
        #         spine.set_color('yellow')
        #         spine.set_linewidth(1)
        # for pix in np.where(np.repeat(pixelmask.bad_hv, 4))[0]:
        #     for key, spine in self.ax_dict[pix].spines.items():
        #         spine.set_visible(True)
        #         spine.set_color('purple')
        #         spine.set_linewidth(1)

    # def plot_waveforms(self, waveforms):
    #     n_pix, n_samples = waveforms.shape
    #
    #     dead = np.logical_or(self.pm.dead, np.repeat(self.pm.bad_hv, 4))
    #     waveforms_notdead = waveforms[~dead]
    #
    #     avg_wf = waveforms_notdead.mean(axis=0)
    #     min_ = waveforms_notdead.min()
    #     max_ = waveforms_notdead.max()
    #
    #     norm = mpl.colors.Normalize(
    #         vmin=waveforms_notdead.max(1).min(),
    #         vmax=waveforms_notdead.max(1).max(),
    #     )
    #
    #     embed()
    #
    #     desc = "Plotting pixels"
    #     for pixel, ax in tqdm(self.ax_dict.items(), desc=desc):
    #         color = mpl.cm.viridis(norm(waveforms[pixel].max()))
    #         ax.set_facecolor(color)
    #         ax.plot(waveforms[pixel], color='white', lw=0.2, alpha=1)
    #         ax.plot(avg_wf, color='black', ls='--', lw=0.2, alpha=0.5)
    #
    #         ax.set_xlim(0, n_samples)
    #         ax.set_ylim(min_, max_)

    # def highlight_turn_off(self, turn_off):
    #     for ipix, t in enumerate(turn_off):
    #         if t:
    #             for key, spine in self.ax_dict[ipix].spines.items():
    #                 spine.set_visible(True)
    #                 spine.set_color('red')
    #                 spine.set_linewidth(1)
    #         # else:
    #         #     for key, spine in self.ax_dict[ipix].spines.items():
    #         #         spine.set_visible(False)
    #
    #     for pix in np.where(turn_off)[0]:
    #         for key, spine in self.ax_dict[pix].spines.items():
    #             spine.set_visible(True)
    #             spine.set_color('red')
    #             spine.set_linewidth(1)

    def save(self, output_path, **kwargs):
        super().save(output_path, **kwargs)
        for ax in self.ax_dict.values():
            ax.lines = []


class GetPlot:
    def __init__(self, mapping, pm_dict):
        self.mapping = mapping
        self.pm_dict = pm_dict
        self.plots = dict()

    def __getitem__(self, item):
        if item not in self.plots:
            self.plots[item] = CameraPlotter(self.mapping, self.pm_dict[item])
        return self.plots[item]


def main():
    paths = dict(
        d190502="/Volumes/ICYBOX/astri_onsky_archive/d2019-06-10_ledflashers/flasher_comparison_May-June/unit0pattern-low_r1.tio",
        d190508="/Volumes/ICYBOX/astri_onsky_archive/d2019-06-10_ledflashers/flasher_comparison_May-June/Run13270_r1.tio",
        d190610="/Volumes/ICYBOX/astri_onsky_archive/d2019-06-10_ledflashers/flasher_comparison_May-June/Run13401_r1.tio",
    )
    readers = {
        key: TIOReader(path, max_events=100)
        for key, path in paths.items()
    }
    waveforms = {
        key: reader[:].mean(0) for key, reader in readers.items()
    }
    mapping = get_superpixel_mapping(readers['d190502'].mapping)

    pixelmasks = dict(
        d190428T2149=PixelMasks(get_calib_data("pixel_masks/d190428T2149.dat")),
    )

    # Calculate coeff
    waveforms_coeff = waveforms['d190502']
    n_pixels, n_samples = waveforms_coeff.shape
    n_sp = n_pixels // 4
    waveforms_sp = waveforms_coeff.reshape(
        (n_sp, 4, n_samples)
    ).sum(1)
    coeff = (waveforms_sp.max(1).mean() / waveforms_sp.max(1))[:, None]

    sp_waveforms = {
        key: wfs.reshape((n_sp, 4, n_samples)).sum(1)
        for key, wfs in waveforms.items()
    }
    sp_waveforms_cal = {
        key: wfs * coeff
        for key, wfs in sp_waveforms.items()
    }

    turn_off = dict()
    for key, wfs in sp_waveforms_cal.items():
        amplitude = wfs.max(1)
        median = np.median(amplitude)
        threshold = median * 1.10
        turn_off[key] = amplitude > threshold

    turn_off['d190610'][[
        355,356,357,358,359,382,375,460,459,457,458,465,289,489,
        502,254,247,154,144,56,46,39,24,25,76]
    ] = True

    for key, sp in turn_off.items():
        print(f"{key}: f{np.where(sp)}")

    plots = GetPlot(mapping, pixelmasks)
    plots['d190428T2149'].highlight_pixels(turn_off['d190502'])
    plots['d190428T2149'].plot_waveforms(sp_waveforms['d190502'])
    plots['d190428T2149'].save(get_plot("d190611_led_flasher/led/d190502.pdf"))
    plots['d190428T2149'].plot_waveforms(sp_waveforms_cal['d190502'])
    plots['d190428T2149'].save(get_plot("d190611_led_flasher/coeff/d190502.pdf"))

    plots['d190428T2149'].highlight_pixels(turn_off['d190508'])
    plots['d190428T2149'].plot_waveforms(sp_waveforms['d190508'])
    plots['d190428T2149'].save(get_plot("d190611_led_flasher/led/d190508.pdf"))
    plots['d190428T2149'].plot_waveforms(sp_waveforms_cal['d190508'])
    plots['d190428T2149'].save(get_plot("d190611_led_flasher/coeff/d190508.pdf"))

    plots['d190428T2149'].highlight_pixels(turn_off['d190610'])
    plots['d190428T2149'].plot_waveforms(sp_waveforms['d190610'])
    plots['d190428T2149'].save(get_plot("d190611_led_flasher/led/d190610.pdf"))
    plots['d190428T2149'].plot_waveforms(sp_waveforms_cal['d190610'])
    plots['d190428T2149'].save(get_plot("d190611_led_flasher/coeff/d190610.pdf"))


if __name__ == '__main__':
    main()
