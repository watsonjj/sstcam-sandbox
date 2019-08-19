from CHECLabPySB import get_data
from CHECLabPySB.d190730_pedestal import Test, all_files
import numpy as np
import pandas as pd
from CHECLabPy.core.io import TIOReader, HDF5Writer
from tqdm import tqdm
from IPython import embed


def process(input_path, output_path, poi):
    r0_reader = TIOReader(input_path)
    n_events = r0_reader.n_events
    n_samples = r0_reader.n_samples
    isam = np.arange(n_samples, dtype=np.uint16)

    df_list = []

    desc = "Looping over events"
    for r0 in tqdm(r0_reader, total=n_events, desc=desc):
        if r0.missing_packets:
            continue

        iev = r0.iev
        fci = r0.first_cell_id
        adc = r0[poi]

        df_list.append(pd.DataFrame(dict(
            iev=iev,
            fci=fci,
            isam=isam,
            adc=adc,
        )))

    df = pd.concat(df_list, ignore_index=True)

    with HDF5Writer(output_path) as writer:
        writer.write(data=df)
        writer.add_metadata(poi=poi)


def process_file(file):
    poi = 30
    r0 = file.r0
    reduced_cell_info = file.reduced_cell_info

    process(r0, reduced_cell_info, poi)


def main():
    # file = Test()
    # process_file(file)

    for file in all_files:
        process_file(file)



if __name__ == '__main__':
    main()
