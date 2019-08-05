from CHECLabPySB import HDF5Writer
from CHECLabPySB.d181008_average_wf import *
import numpy as np
import pandas as pd
from CHECLabPy.core.io import TIOReader
from tqdm import tqdm
from CHECLabPy.utils.waveform import shift_waveform
from IPython import embed


def process(wf_paths, data_path, poi, t_shift):
    df_list = []

    n_files = len(wf_paths)
    for ifile, f in enumerate(wf_paths):
        print("Processing File {}/{}".format(ifile, n_files))
        reader = TIOReader(f, max_events=1000)

        n_events = reader.n_events
        n_samples = reader.n_samples

        wfs = np.zeros((n_events, n_samples))

        desc = "Processing events"
        for wf in tqdm(reader, total=n_events, desc=desc):
            iev = wf.iev
            if t_shift:
                wf = shift_waveform(wf, t_shift)
            wfs[iev] = wf[poi]

        average_wf = wfs.mean(0)

        df_list.append(pd.DataFrame(dict(
            ifile=ifile,
            file=f,
            wf=average_wf,
            isam=np.arange(n_samples)
        )))

    df = pd.concat(df_list, ignore_index=True)

    with HDF5Writer(data_path) as writer:
        writer.write(data=df)
        writer.write_metadata(n_files=n_files)


def process_file(file):
    wf_paths = file.wf_paths
    data_path = file.data_path
    t_shift = file.t_shift
    poi = file.poi
    process(wf_paths, data_path, poi, t_shift)


def main():
    files = [
        # d180514_DynRange_TFPoly(),
        d181004_DynRange_SM_TFNone(),
    ]
    [process_file(f) for f in files]


if __name__ == '__main__':
    main()
