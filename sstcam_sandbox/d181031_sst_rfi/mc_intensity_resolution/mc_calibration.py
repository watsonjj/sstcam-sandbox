from sstcam_sandbox import HDF5Writer
from sstcam_sandbox.d181031_sst_rfi.mc_intensity_resolution import calib_files
import numpy as np
import pandas as pd
from CHECLabPy.core.io import DL1Reader
from numpy.polynomial.polynomial import polyfit
from IPython import embed


def process(file):

    dl1_paths = file.dl1_paths
    pde = file.pde
    mc_calib_path = file.mc_calib_path

    with DL1Reader(dl1_paths[0]) as reader:
        n_pixels = reader.n_pixels
        mapping = reader.mapping
        cols = ['pixel', 'charge', 'mc_true']
        pixel, charge, true = reader.select_columns(cols)
        df = pd.DataFrame(dict(
            pixel=pixel,
            charge=charge,
            true=true,
        ))
        df_agg = df.groupby(['pixel', 'true']).agg({'charge': ['mean', 'std']}).reset_index()
        pixels = np.where(df.groupby('pixel').sum()['true'].values > 1000)[0]

    m_array = np.full(n_pixels, np.nan)
    for p in pixels:
        df_p = df_agg.loc[(df_agg['pixel'] == p) & (df_agg['true'] > 0)]
        x = df_p['true'].values / pde
        y = df_p['charge']['mean'].values
        yerr = df_p['charge']['std'].values
        yerr[np.isnan(yerr)] = 1000
        yerr[yerr == 0] = 1000
        c, m = polyfit(x, y, [1], w=y/yerr)
        m_array[p] = m

    df_calib = pd.DataFrame(dict(
        pixel=np.arange(n_pixels),
        mc_m=m_array,
    ))

    df_calib_mean = df_calib.copy()
    df_calib_mean['mc_m'] = np.nanmean(m_array)

    print("Average Gradient = {}".format(np.nanmean(m_array)))

    with HDF5Writer(mc_calib_path) as writer:
        writer.write(data=df_calib)
        writer.write_mapping(mapping)
        writer.write_metadata(n_pixels=n_pixels)


def main():
    [process(f) for f in calib_files]


if __name__ == '__main__':
    main()
