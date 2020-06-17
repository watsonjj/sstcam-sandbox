from os.path import join, abspath, dirname
import numpy as np
import pandas as pd
from CHECLabPy.plotting.camera import CameraImage
from CHECLabPy.calib import TimeCalibrator, PixelMasks
from CHECLabPy.core.io import TIOReader
from CHECLabPy.waveform_reducers.timing import Timing
from tqdm import tqdm


DIR = abspath(dirname(__file__))


def main():
    path = "/Users/Jason/Data/d2019-04-23_nudges/bright_50pe/Run09095_r1.tio"
    reader = TIOReader(path)
    n_events = reader.n_events
    n_pixels = reader.n_pixels
    n_samples = reader.n_samples
    pixel_array = np.arange(n_pixels)
    time_calibrator = TimeCalibrator()
    extractor = Timing(n_pixels, n_samples)
    df_list = []
    for wfs in tqdm(reader, total=n_events):
        iev = wfs.iev
        shifted = time_calibrator(wfs)

        params = extractor.process(wfs)
        params_shifted = extractor.process(shifted)

        df_list.append(pd.DataFrame(dict(
            iev=iev,
            pixel=pixel_array,
            t_pulse=params['t_pulse'],
            t_pulse_corrected=params_shifted['t_pulse'],
        )))

    df = pd.concat(df_list, ignore_index=True)

    pm = PixelMasks()
    dead = np.where(pm.all_mask)
    mask = ~np.isin(df['pixel'].values, dead)
    df = df.iloc[mask]
    df_ev = df.groupby('iev').mean()
    mean_timing = np.repeat(df_ev['t_pulse'], n_pixels - pm.all_mask.sum())
    mean_timing_c = np.repeat(df_ev['t_pulse'], n_pixels - pm.all_mask.sum())
    df['t_pulse'] -= mean_timing.values
    df['t_pulse_corrected'] -= mean_timing_c.values
    df_pix = df.groupby('pixel').mean()
    pixel = df_pix.index.values
    t_pulse = df_pix['t_pulse'].values
    t_pulse_corrected = df_pix['t_pulse_corrected'].values

    image = np.full(n_pixels, np.nan)
    image[pixel] = t_pulse
    mean = np.nanmean(image)
    std = np.nanstd(image)
    ci = CameraImage.from_mapping(reader.mapping)
    ci.image = image
    ci.add_colorbar()
    ci.ax.set_title(f"MEAN = {mean:.2f}, STDDEV = {std:.2f}")
    ci.save(join(DIR, "before.pdf"))

    image = np.full(n_pixels, np.nan)
    image[pixel] = t_pulse_corrected
    mean = np.nanmean(image)
    std = np.nanstd(image)
    ci = CameraImage.from_mapping(reader.mapping)
    ci.image = image
    ci.add_colorbar()
    ci.ax.set_title(f"MEAN = {mean:.2f}, STDDEV = {std:.2f}")
    ci.save(join(DIR, "after.pdf"))


if __name__ == '__main__':
    main()
