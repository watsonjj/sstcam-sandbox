import argparse
from argparse import ArgumentDefaultsHelpFormatter as Formatter
import re
import os
import numpy as np
import pandas as pd
from tqdm import tqdm
from CHECLabPy.core.io import DL1Reader
from IPython import embed


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


def open_runlist(path):
    df = pd.read_csv(path,
                     header=None,
                     names=['run', 'attenuation', 'illumination', 'n_events',
                            '???'], delimiter=' ', index_col=0, comment='#',
                     dtype={'run': np.int, 'attenuation': np.float,
                            'illumination': np.float, 'n_events': np.int,
                            '???': str}
                     )
    input_dir = os.path.dirname(path)
    input_run_path = os.path.join(input_dir, "Run{:05d}_dl1.h5")
    df['path'] = [input_run_path.format(i) for i in df.index]
    return df


def obtain_readers(df_runs):
    files = df_runs['path'].values
    df_runs['reader'] = [DL1Reader(fp) for fp in files]


# class TimeCorrection:
#     def __init__(self):
#         self._df_list = []
#         self._df = pd.DataFrame()
#         self._n_bytes = 0
#
#     def add(self, amplitude, df_e):
#         pixel = df_e['pixel'].values
#         t_event = df_e[['t_pulse', 'iev']].groupby('iev').transform('mean')
#         t_correction_ev = df_e['t_pulse'].values - t_event.values[:, 0]
#
#         df = pd.DataFrame(dict(
#             pixel=pixel,
#             amplitude=amplitude,
#             sum=t_correction_ev,
#             sum2=t_correction_ev**2,
#             n=np.uint32(1)
#         ))
#         self._df_list.append(df)
#         self._n_bytes += df.memory_usage(index=True, deep=True).sum()
#         if self._n_bytes > 0.5E9:
#             self.amalgamate()
#
#     def amalgamate(self):
#         self._df = pd.concat([self._df, *self._df_list], ignore_index=True)
#         self._df = self._df.groupby(['pixel', 'amplitude']).sum().reset_index()
#         self._n_bytes = 0
#         self._df_list = []
#
#     def finish(self):
#         self.amalgamate()
#         df = self._df.copy()
#         sum_ = df['sum'].values
#         sum2 = df['sum2'].values
#         n = df['n'].values
#         mean = sum_/n
#         std = np.sqrt((sum2 / n) - (mean**2))
#         df['t_correction'] = mean
#         df['t_correction_std'] = std
#         return df


def main():
    description = 'Create a new HDFStore file containing the time corrections'
    parser = argparse.ArgumentParser(description=description,
                                     formatter_class=Formatter)
    parser.add_argument('-f', '--file', dest='input_path',
                        action='store', required=True,
                        help='paths to the runlist txt file')
    parser.add_argument('-o', '--output', dest='output_path',
                        action='store', required=True,
                        help='path to store the output HDFStore file')
    args = parser.parse_args()

    input_path = args.input_path
    output_path = args.output_path

    df_runs = open_runlist(input_path)
    obtain_readers(df_runs)

    # amplitudes = obtain_amplitude_from_filename(files)

    # assert len(readers) == len(amplitudes)

    if os.path.exists(output_path):
        os.remove(output_path)

    # tc = TimeCorrection()
    mapping = df_runs.iloc[0]['reader'].mapping

    print("Created HDFStore file: {}".format(output_path))

    with pd.HDFStore(output_path) as store:
        store['mapping'] = df_runs.iloc[0]['reader'].store['mapping']
        store.get_storer('mapping').attrs.metadata = df_runs.iloc[0]['reader'].store.get_storer('mapping').attrs.metadata

        mean_list = []

        desc = "Looping over files"
        n_rows = df_runs.index.size
        for index, row in tqdm(df_runs.iterrows(), total=n_rows, desc=desc):
            reader = row['reader']
            amplitude = row['illumination']
            attenuation = row['attenuation']

            df = reader.load_entire_table()
            df_mean = df.groupby('pixel').mean().reset_index()
            df_mean['attenuation'] = attenuation
            df_mean['amplitude'] = amplitude

            mean_list.append(df_mean)

            reader.store.close()

        store['mean'] = pd.concat(mean_list, ignore_index=True)

    print("Filled file: {}".format(output_path))


if __name__ == '__main__':
    main()
