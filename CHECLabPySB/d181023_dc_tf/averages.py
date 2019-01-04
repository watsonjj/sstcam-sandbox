from CHECLabPySB.d181023_dc_tf import all_files
from CHECLabPySB import get_data, HDF5Writer
from CHECLabPy.core.io import TIOReader
import numpy as np
import pandas as pd
from tqdm import trange
from IPython import embed


def get_df(paths, vped_list):
    assert (len(paths) == len(vped_list))
    readers = [TIOReader(p) for p in paths]

    n_files = len(paths)
    first_reader = TIOReader(paths[0])
    n_pixels = first_reader.n_pixels
    n_samples = first_reader.n_samples

    # mean = np.zeros((n_files, n_pixels, n_samples))
    # std = np.zeros((n_files, n_pixels, n_samples))
    # vped = np.zeros((n_files, n_pixels, n_samples))
    jpixel, jsample = np.indices((n_pixels, n_samples))

    df_list = []

    for ifile in trange(n_files):
        reader = readers[ifile]

        r_n_events = reader.n_events
        r_n_pixels = reader.n_pixels
        r_n_samples = reader.n_samples
        samples = np.zeros((r_n_events, r_n_pixels, r_n_samples))
        for iev, wf in enumerate(reader):
            samples[iev] = wf

        mean = np.mean(samples, 0)
        std = np.std(samples, 0)
        vped = vped_list[ifile]

        df_list.append(pd.DataFrame(dict(
            vped_dac=vped,
            pixel=jpixel.ravel(),
            sample=jsample.ravel(),
            mean=mean.ravel(),
            std=std.ravel(),
        )))

    df = pd.concat(df_list, ignore_index=True)

    return df


def process(file):
    r0_paths = file.r0_paths
    tfnone_paths = file.tfnone_paths
    tfpoly_paths = file.tfpoly_paths
    vped_list = file.vped_list
    output_path = file.averages_path

    try:
        r0_df = get_df(r0_paths, vped_list)
        tfnone_df = get_df(tfnone_paths, vped_list)
        tfpoly_df = get_df(tfpoly_paths, vped_list)
    except:
        embed()


    with HDF5Writer(output_path) as writer:
        writer.write(
            r0=r0_df,
            tfnone=tfnone_df,
            tfpoly_df=tfpoly_df,
        )


def main():
    [process(f) for f in all_files]


if __name__ == '__main__':
    main()