from CHECLabPy.core.io import HDF5Reader, HDF5Writer
from sstcam_sandbox import get_data
from CHECLabPy.calib.pixel_masks import PixelMasks
from os.path import dirname, abspath, join
import numpy as np
from numpy.polynomial.polynomial import polyfit
import pandas as pd
from IPython import embed


DIR = abspath(dirname(__file__))


def process(path, dead, output):
    with HDF5Reader(path) as reader:
        df = reader.read("data")
        df = df.loc[~df['pixel'].isin(dead)]

    d_list = []

    extractors = set(df.columns) - {'iobs', 'iev', 'pixel', 'true'}
    for extractor in extractors:
        gt5 = df['true'].values > 5
        true = df['true'].values[gt5]
        measured = df[extractor].values[gt5]
        coeff = polyfit(true, measured, [1])
        _, calib = coeff
        df[extractor] /= calib

        for true, group in df.groupby("true"):
            n = group.index.size
            d_list.append(dict(
                extractor=extractor,
                true=true,
                n=n,
                mean=group[extractor].mean(),
                std=group[extractor].std(),
                rmse=np.sqrt(np.sum((group[extractor]-true)**2)/n),
                res=np.sqrt(np.sum((group[extractor]-true)**2) / n + true),
            ))

    df_cr = pd.DataFrame(d_list)

    with HDF5Writer(output) as writer:
        writer.write(data=df_cr)


def main():
    path = get_data("d190520_charge_extraction/mc/charge.h5")
    pm = PixelMasks(join(DIR, "mc_chec_pixel_mask_190521.dat"))
    dead = np.where(pm.all_mask)[0]
    output = get_data("d190520_charge_extraction/mc/analysis.h5")
    process(path, dead, output)


if __name__ == '__main__':
    main()
