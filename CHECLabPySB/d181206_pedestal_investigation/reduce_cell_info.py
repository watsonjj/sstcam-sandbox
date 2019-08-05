from CHECLabPySB import get_data, HDF5Writer
import numpy as np
import pandas as pd
from CHECLabPy.core.io import TIOReader
from tqdm import tqdm
from CHECLabPySB.d181206_pedestal_investigation import *
# from matplotlib import pyplot as plt


def process(input_path, output_path, poi):
    r0_reader = TIOReader(input_path)
    n_events = r0_reader.n_events
    n_samples = r0_reader.n_samples
    samples = np.arange(n_samples, dtype=np.uint16)

    df_list = []

    desc = "Looping over events"
    for r0 in tqdm(r0_reader, total=n_events, desc=desc):
        iev = r0.iev
        fci = r0.first_cell_id[poi].item()

        df_list.append(pd.DataFrame(dict(
            iev=iev,
            fci=fci,
            isam=samples,
            r0=r0[poi],
        )))

    df = pd.concat(df_list, ignore_index=True)

    with HDF5Writer(output_path) as writer:
        writer.write(data=df)
        writer.write_metadata(poi=poi)


def process_file(file):
    name = file.__class__.__name__
    input_path = file.r0_path
    output_path = get_data("d181206_pedestal_investigation/cell_info/{}.h5".format(name))
    poi = 10
    process(input_path, output_path, poi)


def main():
    files = [
        # Pedestal_SN0038_Erlangen_23deg_OldFW_3blocks(),
        # Pedestal_SN0038_Erlangen_AC_23deg_OldFW_3blocks(),
        # Pedestal_SN0038_Erlangen_AC_40deg_OldFW_3blocks(),
        # Pedestal_SN0038_Erlangen_23deg_NewFW_3blocks(),
        # Pedestal_SN0038_Erlangen_23deg_NewFW_waitlong_3blocks(),
        # Pedestal_SN0038_Erlangen_23deg_NewFW_4blocks(),
        # Pedestal_SN0038_Erlangen_AC_23deg_NewFW_4blocks(),
        # Pedestal_SN0038_Erlangen_30deg_NewFW_4blocks(),
        # Pedestal_SN0038_MPIK_23deg_NewFW_4blocks_500Hz(),
        # Pedestal_SN0038_MPIK_23deg_NewFW_4blocks_1000Hz(),
        # Pedestal_SN0038_MPIK_23deg_NewFW_4blocks_2000Hz(),
        # Pedestal_SN0038_MPIK_23deg_NewFW_4blocks_4000Hz(),
        # Pedestal_SN0038_MPIK_23deg_NewFW_4blocks_3000Hz_cvped(),
        # Pedestal_SN0038_MPIK_23deg_NewFW_4blocks_3500Hz_cvped(),
        # Pedestal_SN0038_MPIK_23deg_NewFW_4blocks_4000Hz_cvped(),
        Pedestal_Adrian(),
    ]
    [process_file(f) for f in files]


if __name__ == '__main__':
    main()
