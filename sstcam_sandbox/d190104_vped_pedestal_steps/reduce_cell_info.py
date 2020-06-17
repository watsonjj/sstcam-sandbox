from sstcam_sandbox import get_data, HDF5Writer
from sstcam_sandbox.utils.stdout import stdout_redirector
import numpy as np
import pandas as pd
from CHECLabPy.core.io import TIOReader
from tqdm import tqdm
from sstcam_sandbox.d190104_vped_pedestal_steps import *
from multiprocessing import Pool
import os
from IPython import embed
from functools import partial
from target_calib import CalculateRowColumnBlockPhase, GetCellIDTCArray


class ReducedDataframe:
    def __init__(self):
        self._df_list = []
        self._df = pd.DataFrame()
        self._n_bytes = 0

    def add(self, amplitude, sample, fci, isam):
        df = pd.DataFrame(dict(
            amplitude=amplitude,
            fci=fci,
            isam=isam,
            sum=sample,
            sum2=sample**2,
            n=np.uint32(1)
        ))
        self._df_list.append(df)
        # self._n_bytes += df.memory_usage(index=True, deep=True).sum()
        # if self._n_bytes > 1E9:
        #     self.amalgamate()

    def amalgamate(self):
        grouping = ['amplitude', 'fci', 'isam']

        self._df = pd.concat([self._df, *self._df_list], ignore_index=True)
        self._df = self._df.groupby(grouping).sum().reset_index()
        self._n_bytes = 0
        self._df_list = []

    def finish(self):
        self.amalgamate()
        df = self._df.copy()
        sum_ = df['sum'].values
        sum2 = df['sum2'].values
        n = df['n'].values
        mean = sum_ / n
        std = np.sqrt((sum2 / n) - (mean**2))
        df['mean'] = mean
        df['std'] = std
        return df


def process(entry, poi):
    with stdout_redirector():
        input_path, amplitude = entry
        df_list = []
        desc = "Looping over events"
        r0_reader = TIOReader(input_path)
        n_events = r0_reader.n_events
        n_samples = r0_reader.n_samples
        isam = np.arange(n_samples, dtype=np.uint16)

        rd = ReducedDataframe()

        for r0 in r0_reader:
            fci = r0.first_cell_id[poi].item()
            rd.add(amplitude, r0[poi].astype(np.int), fci, isam)

        df = rd.finish()

    return df


def process_list(input_paths, amplitudes, output_path, poi):
    desc = "Looping over files"

    process_poi = partial(process, poi=poi)

    it = list(zip(input_paths, amplitudes))[::4]
    with Pool(int(os.cpu_count() - 2)) as pool:
        process_pool = pool.imap(process_poi, it)
        df_list = list(tqdm(process_pool, total=len(it), desc=desc))
    # for i in it:
    #     process_poi(i)

    df = pd.concat(df_list, ignore_index=True)

    with HDF5Writer(output_path) as writer:
        writer.write(data=df)
        writer.write_metadata(poi=poi)


def process_file(file):
    name = file.__class__.__name__
    input_paths = file.r0_paths
    amplitudes = file.amplitudes
    output_path = get_data("d190104_vped_pedestal_steps/cell_info/{}.h5".format(name))
    poi = 10

    assert len(input_paths) > 0

    process_list(input_paths, amplitudes, output_path, poi)


def main():
    files = [
        DC_TF_ExtSync_23deg(),
    ]
    [process_file(f) for f in files]


if __name__ == '__main__':
    main()
