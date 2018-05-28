import argparse
from argparse import ArgumentDefaultsHelpFormatter as Formatter
import re
import os
import numpy as np
import pandas as pd
from tqdm import tqdm
from CHECLabPy.core.io import DL1Reader
from CHECLabPy.utils.resolutions import ChargeResolution


def commonsuffix(files):
    reveresed = [f[::-1] for f in files]
    return os.path.commonprefix(reveresed)[::-1]


def obtain_amplitude_from_filename(files):
    commonprefix = os.path.commonprefix
    pattern = commonprefix(files) + '(.+?)' + commonsuffix(files)
    amplitudes = []
    for fp in files:
        try:
            reg_exp = re.search(pattern, fp)
            if reg_exp:
                amplitudes.append(reg_exp.group(1))
        except AttributeError:
            print("Problem with Regular Expression, "
                  "{} does not match patten {}".format(fp, pattern))
    return amplitudes


def obtain_readers(files):
    return [DL1Reader(fp) for fp in files]


def main():
    description = 'Create a new HDFStore file containing the charge resolution'
    parser = argparse.ArgumentParser(description=description,
                                     formatter_class=Formatter)
    parser.add_argument('-f', '--files', dest='input_paths',
                        nargs='+', help='paths to the input dl1 HDF5 files')
    parser.add_argument('-o', '--output', dest='output_path',
                        action='store', required=True,
                        help='path to store the output HDFStore file')
    parser.add_argument('-c', '--column', dest='charge_column',
                        action='store', default='charge',
                        help='column from the input tables to use as the '
                             'extracted charge')
    args = parser.parse_args()

    files = args.input_paths
    output_path = args.output_path
    column = args.charge_column

    readers = obtain_readers(files)
    amplitudes = obtain_amplitude_from_filename(files)

    assert len(readers) == len(amplitudes)

    if os.path.exists(output_path):
        os.remove(output_path)

    cr = ChargeResolution()

    print("Created HDFStore file: {}".format(output_path))

    with pd.HDFStore(output_path) as store:
        desc = "Looping over files"
        iter_z = zip(readers, amplitudes)
        for r, amp in tqdm(iter_z, total=len(readers), desc=desc):
            for df in r.iterate_over_chunks():
                df = df[[column, "pixel"]]
                df = df.rename(columns={column: "measured"})
                df['true'] = np.float32(amp)
                store.append('charge', df, index=False)
                cr.add(
                    df['pixel'].values,
                    df['true'].values,
                    df['measured'].values
                )
            r.store.close()
        df, df_camera = cr.finish()
        store['charge_resolution_pixel'] = df
        store['charge_resolution_camera'] = df_camera

    print("Filled file with charge resolution: {}".format(output_path))


if __name__ == '__main__':
    main()
