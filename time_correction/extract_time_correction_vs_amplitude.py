import argparse
from argparse import ArgumentDefaultsHelpFormatter as Formatter
import re
import os
import numpy as np
import pandas as pd
from tqdm import tqdm
from CHECLabPy.core.io import DL1Reader


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


class TimeCorrection:
    def __init__(self):
        self._df_list = []
        self._df = pd.DataFrame()
        self._n_bytes = 0

    def add(self, amplitude, df_e):
        pixel = df_e['pixel'].values
        t_event = df_e[['t_pulse', 'iev']].groupby('iev').transform('mean')
        t_correction_ev = df_e['t_pulse'].values - t_event.values[:, 0]

        df = pd.DataFrame(dict(
            pixel=pixel,
            amplitude=amplitude,
            sum=t_correction_ev,
            sum2=t_correction_ev**2,
            n=np.uint32(1)
        ))
        self._df_list.append(df)
        self._n_bytes += df.memory_usage(index=True, deep=True).sum()
        if self._n_bytes > 0.5E9:
            self.amalgamate()

    def amalgamate(self):
        self._df = pd.concat([self._df, *self._df_list], ignore_index=True)
        self._df = self._df.groupby(['pixel', 'amplitude']).sum().reset_index()
        self._n_bytes = 0
        self._df_list = []

    def finish(self):
        self.amalgamate()
        df = self._df.copy()
        sum_ = df['sum'].values
        sum2 = df['sum2'].values
        n = df['n'].values
        mean = sum_/n
        std = np.sqrt((sum2 / n) - (mean**2))
        df['t_correction'] = mean
        df['t_correction_std'] = std
        return df


def main():
    description = 'Create a new HDFStore file containing the time corrections'
    parser = argparse.ArgumentParser(description=description,
                                     formatter_class=Formatter)
    parser.add_argument('-f', '--files', dest='input_paths',
                        nargs='+', help='paths to the input dl1 HDF5 files')
    parser.add_argument('-o', '--output', dest='output_path',
                        action='store', required=True,
                        help='path to store the output HDFStore file')
    args = parser.parse_args()

    files = args.input_paths
    output_path = args.output_path

    readers = obtain_readers(files)
    amplitudes = obtain_amplitude_from_filename(files)

    assert len(readers) == len(amplitudes)

    if os.path.exists(output_path):
        os.remove(output_path)

    tc = TimeCorrection()
    mapping = readers[0].mapping

    print("Created HDFStore file: {}".format(output_path))

    with pd.HDFStore(output_path) as store:
        store['mapping'] = readers[0].store['mapping']
        store.get_storer('mapping').attrs.metadata = readers[0].store.get_storer('mapping').attrs.metadata
        desc = "Looping over files"
        iter_z = zip(readers, amplitudes)
        for r, amp in tqdm(iter_z, total=len(readers), desc=desc):
            n_pixels = r.n_pixels
            for df_event in r.iterate_over_chunks(n_pixels*10000):
                tc.add(
                    np.float32(amp),
                    df_event
                )
            r.store.close()
        df = tc.finish()
        store['t_correction'] = df

    print("Filled file with time correction: {}".format(output_path))


if __name__ == '__main__':
    main()
