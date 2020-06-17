from os.path import join, abspath, dirname
import numpy as np
import pandas as pd
from CHECLabPy.calib import PixelMasks, get_calib_data


DIR = abspath(dirname(__file__))


def calculate_t_cor(pixel, t_pulse):
    t_pulse_camera = np.zeros(2048)
    t_pulse_camera[pixel] = t_pulse
    pm = PixelMasks()
    t_pulse_camera[pm.all_mask] = np.nan
    t_pulse_camera[t_pulse_camera == 0] = np.nan
    t_cor_tm = np.nanmean(t_pulse_camera.reshape((32, 64)), 0)
    t_cor = t_cor_tm.mean() - t_cor_tm
    t_cor = np.tile(t_cor, 32).ravel()
    t_cor[:2048 // 2] -= 0.76
    t_cor[2048 // 2:] += 0.76
    return t_cor


def main():
    df = pd.read_csv(join(DIR, "t_pulse.cfg"), sep=' ')
    pixel = df['Pixel'].values
    t_pulse = df['t_pulse'].values
    t_cor = calculate_t_cor(pixel, t_pulse)

    df = pd.DataFrame(dict(pixel=np.arange(t_cor.size), t_cor=t_cor))
    df.to_csv(get_calib_data("time_correction.dat"), sep='\t', index=False)


if __name__ == '__main__':
    main()
