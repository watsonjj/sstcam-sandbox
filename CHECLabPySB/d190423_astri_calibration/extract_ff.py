from CHECLabPySB import get_astri_2019
from os.path import join
import numpy as np
import pandas as pd
from CHECLabPy.calib import PixelMasks
from CHECLabPy.core.io import HDF5Reader
from CHECLabPy.plotting.camera import CameraImage
from CHECOnsky.calib import get_calib_data


def main():
    pm = PixelMasks()
    dead = np.where(np.logical_or(pm.dead, np.repeat(pm.bad_hv, 4)))[0]

    bright_path = get_astri_2019("d2019-04-23_nudges/bright_50pe/charge.h5")
    with HDF5Reader(bright_path) as reader:
        df = reader.read("data").groupby(
            ['nudge', 'pixel']
        ).mean().reset_index()
        mapping = reader.get_mapping()

    df_0 = df.loc[df['nudge'] == 0]
    isin_dead = df_0['pixel'].isin(dead)
    avg = df_0.loc[~isin_dead].mean()
    ff = avg['onsky_calib'] / df_0['onsky_calib'].values
    ff[dead] = 1

    np.testing.assert_allclose(ff.mean(), 1, rtol=1e-2)

    df = pd.DataFrame(dict(
        pixel=np.arange(ff.size),
        ff=ff,
    ))

    output_dir = get_astri_2019("d2019-04-23_nudges/results/extract_ff")
    cm = CameraImage.from_mapping(mapping)
    cm.image = ff
    cm.add_colorbar()
    cm.highlight_pixels(pm.dead, 'red')
    cm.highlight_pixels(np.repeat(pm.bad_hv, 4), 'black')
    cm.highlight_pixels(pm.low, 'blue')
    cm.save(join(output_dir, "ff_camera.pdf"))

    outpath = get_calib_data("ff_coeff.dat")
    df.to_csv(outpath, sep='\t', index=False)
    print(f"Created ff_coeff file: {outpath}")


if __name__ == '__main__':
    main()
