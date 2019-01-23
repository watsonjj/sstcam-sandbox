from CHECLabPySB.d190117_trigger_stability import *
from CHECLabPySB import get_data, HDF5Writer
from CHECLabPy.core.io import TIOReader
from target_calib import MappingSP, CameraConfiguration
import numpy as np
import pandas as pd
from tqdm import tqdm
from matplotlib import pyplot as plt
from IPython import embed


def process(readers, output_path):

    df_list = []

    desc0 = "Looping over files"
    desc1 = "Looping over events"
    for reader in tqdm(readers, total=len(readers), desc=desc0):
        mapping = reader.mapping
        sp_arr = np.vstack(mapping.groupby("superpixel").pixel.apply(np.array))
        n_events = reader.n_events
        n_pixels = reader.n_pixels
        pixels = np.arange(n_pixels)

        for wfs in tqdm(reader, total=n_events, desc=desc1):
            iev = reader.index
            if iev % 10:
                continue
            t_cpu_sec = reader.current_cpu_s
            t_cpu_ns = reader.current_cpu_ns
            t_cpu = pd.to_datetime(
                np.int64(t_cpu_sec * 1E9) + np.int64(t_cpu_ns),
                unit='ns'
            )

            amplitude = wfs.max(axis=1)
            sum_wfs = wfs[sp_arr].sum(1)
            amplitude_sp = sum_wfs.max(axis=1)

            # plt.plot(wfs[sp_arr][372].T)
            # plt.ylim((-25, 75))
            # plt.pause(0.5)
            # plt.cla()

            df_list.append(pd.DataFrame(dict(
                iev=iev,
                t_cpu=t_cpu,
                pixel=pixels,
                amplitude=amplitude,
                amplitude_sp=np.repeat(amplitude_sp, 4),
            )))

    df = pd.concat(df_list, ignore_index=True)

    with HDF5Writer(output_path) as writer:
        writer.write(data=df)
        writer.write_mapping(readers[0].mapping)


def process_file(file):
    readers = file.tio_readers
    name = file.__class__.__name__
    output_path = get_data("d190117_trigger_stability/{}/amplitudes.h5".format(name))
    process(readers, output_path)


def main():
    files = [
        # d190111(),
        # d190118(),
        d190121(),
    ]
    [process_file(file) for file in files]


if __name__ == '__main__':
    main()
