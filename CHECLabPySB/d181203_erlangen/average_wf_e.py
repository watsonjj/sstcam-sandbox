from CHECLabPySB import HDF5Writer
from CHECLabPySB.d181203_erlangen.files.dc_tf import *
from CHECLabPySB.d181203_erlangen.files.ac_tf import *
from CHECLabPySB.d181203_erlangen.files.dynrange import *
import numpy as np
import pandas as pd
from CHECLabPy.core.io import TIOReader
from tqdm import tqdm
from CHECLabPy.utils.waveform import shift_waveform
from IPython import embed


def process(input_paths, data_path, poi):
    df_list = []

    n_files = len(input_paths)
    for ifile, f in enumerate(input_paths):
        print("Processing File {}/{}".format(ifile, n_files))
        reader = TIOReader(f, max_events=1000)

        n_events = reader.n_events
        n_samples = reader.n_samples

        wfs = np.zeros((n_events, n_samples))

        desc = "Processing events"
        for wf in tqdm(reader, total=n_events, desc=desc):
            iev = wf.iev
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
    input_paths = file.r0_paths
    name = file.__class__.__name__
    output_path = get_data("d181203_erlangen/average_wf/{}.h5".format(name))
    poi = file.poi
    process(input_paths, output_path, poi)


def main():
    files = [
        # DC_TF_ExtSync_23deg(),
        # DC_TF_HardSync_23deg(),
        # AC_TF_23deg(),
        DynRange_23deg(),
    ]
    [process_file(f) for f in files]


if __name__ == '__main__':
    main()
