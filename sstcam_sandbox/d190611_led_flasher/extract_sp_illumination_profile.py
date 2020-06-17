from sstcam_sandbox import get_astri_2019
from CHECLabPy.core.io import TIOReader
import numpy as np
import pandas as pd
from os.path import dirname, abspath, join


DIR = abspath(dirname(__file__))


def main():
    path = get_astri_2019("d2019-06-10_ledflashers/flasher_comparison_May-June/unit0pattern-low_r1.tio")
    reader = TIOReader(path, max_events=100)
    waveforms = reader[:].mean(0)

    # Calculate coeff
    n_pixels, n_samples = waveforms.shape
    n_sp = n_pixels // 4
    waveforms_sp = waveforms.reshape(
        (n_sp, 4, n_samples)
    ).sum(1)
    correction = (waveforms_sp.max(1).mean() / waveforms_sp.max(1))

    df = pd.DataFrame(dict(
        superpixel=np.arange(n_sp),
        correction=correction,
    ))
    df.to_csv(join(DIR, "sp_illumination_profile.dat"), sep='\t', index=False)


if __name__ == '__main__':
    main()
