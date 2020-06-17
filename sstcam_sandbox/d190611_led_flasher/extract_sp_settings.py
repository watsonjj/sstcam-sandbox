from sstcam_sandbox import get_astri_2019
from CHECLabPy.core.io import TIOReader
from CHECLabPy.plotting.waveform import CameraPixelWaveformPlotter
from CHECLabPy.utils.mapping import get_superpixel_mapping
import numpy as np
import pandas as pd
from os.path import dirname, abspath, join


DIR = abspath(dirname(__file__))


class CameraPlotter(CameraPixelWaveformPlotter):
    def __init__(self, mapping):
        super().__init__(mapping)

    def save(self, output_path, **kwargs):
        super().save(output_path, **kwargs)
        for ax in self.ax_dict.values():
            ax.lines = []


def main():
    # path = get_astri_2019("d2019-06-10_ledflashers/flasher_comparison_May-June/unit0pattern-low_r1.tio")
    # path = get_astri_2019("d2019-06-10_ledflashers/flasher_comparison_May-June/Run13270_r1.tio")
    path = get_astri_2019("d2019-06-10_ledflashers/flasher_comparison_May-June/Run13401_r1.tio")

    output_dir = path.replace("_r1.tio", "")
    reader = TIOReader(path, max_events=100)
    waveforms = reader[:].mean(0)
    mapping = get_superpixel_mapping(reader.mapping)
    n_pixels, n_samples = waveforms.shape
    n_sp = n_pixels // 4

    correction = pd.read_csv(
        join(DIR, "sp_illumination_profile.dat"), sep='\t'
    )['correction'].values

    sp_waveforms = waveforms.reshape((n_sp, 4, n_samples)).sum(1)
    sp_waveforms_corrected = sp_waveforms * correction[:, None]

    amplitude = sp_waveforms_corrected.max(1)
    median = np.median(amplitude)
    threshold = median * 1.10
    trigger_off = amplitude > threshold
    # trigger_off[[  # TODO: Remove?
    #     355, 356, 357, 358, 359, 382, 375, 460, 459, 457, 458, 465, 289, 489,
    #     502, 254, 247, 154, 144, 56, 46, 39, 24, 25, 76
    # ]] = True
    hv_off = np.zeros(n_sp, dtype=bool)
    hv_off[[24, 453]] = True
    print(f"SP Trigger OFF: {np.where(trigger_off)[0].tolist()}")
    print(f"SP HV OFF: {np.where(hv_off)[0].tolist()}")

    plot = CameraPlotter(mapping)
    plot.highlight_pixels(trigger_off, 'yellow')
    plot.highlight_pixels(hv_off, 'red')
    plot.plot_waveforms(sp_waveforms)
    plot.save(join(output_dir, "led.pdf"))
    plot.plot_waveforms(sp_waveforms_corrected)
    plot.save(join(output_dir, "uniform.pdf"))

    df = pd.DataFrame(dict(
        superpixel=np.arange(n_sp),
        hv_on=(~hv_off).astype(int),
        trigger_off=trigger_off.astype(int),
    ))
    df.to_csv(
        join(output_dir, "sp_settings.txt"),
        sep='\t', index=False
    )


if __name__ == '__main__':
    main()
