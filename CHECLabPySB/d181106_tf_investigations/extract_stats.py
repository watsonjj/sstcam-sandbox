from CHECLabPySB.d181106_tf_investigations import all_files
from CHECLabPySB import HDF5Writer, HDF5Reader
import pandas as pd
from tqdm import tqdm
from CHECLabPy.utils.files import open_runlist_dl1
import numpy as np


def rmse(measured, true):
    return np.sqrt(np.sum(np.power(measured - true, 2)) / measured.size )


def charge_resolution_df(group):
    return rmse(group['measured'], group['true'])


def rms_charge_df(group):
    return rmse(group['charge'], group['charge_mean'])


def rms_measured_df(group):
    return rmse(group['measured'], group['measured_mean'])


def process(file):
    runlist_path = file.runlist_path
    fw_path = file.fw_path
    ff_path = file.ff_path
    output_path = file.stats_path

    df_runs = open_runlist_dl1(runlist_path)
    df_runs['transmission'] = 1/df_runs['fw_atten']
    n_runs = df_runs.index.size
    mapping = df_runs.iloc[0]['reader'].mapping
    n_pixels = df_runs.iloc[0]['reader'].n_pixels

    with HDF5Reader(fw_path) as reader:
        df = reader.read("data")
        fw_m = df['fw_m'].values
        fw_merr = df['fw_merr'].values

    with HDF5Reader(ff_path) as reader:
        df = reader.read("data")
        ff_m = df['ff_m'].values
        ff_c = df['ff_c'].values

    df_list = []

    desc0 = "Looping over files"
    it = enumerate(df_runs.iterrows())
    for i, (run, row) in tqdm(it, total=n_runs, desc=desc0):
        reader = row['reader']
        transmission = row['transmission']
        fw_pos = row['fw_pos']
        n_rows = n_pixels * 1000
        pixel, charge = reader.select_columns(['pixel', 'charge'], stop=n_rows)
        true = transmission * fw_m[pixel]

        df = pd.DataFrame(dict(
            pixel=pixel,
            charge=charge,
            measured=(charge - ff_c[pixel]) / ff_m[pixel],
            run=run,
            transmission=transmission,
            fw_pos=fw_pos,
            true=true,
        ))
        trans = df.groupby('pixel').transform('mean')
        df['charge_mean'] = trans['charge']
        df['measured_mean'] = trans['measured']

        gb = df.groupby('pixel')

        df_stats = gb.agg({'charge': ['mean', 'std'], 'measured': ['mean', 'std']})
        df_stats['run'] = run
        df_stats['transmission'] = transmission
        df_stats['fw_pos'] = fw_pos
        df_stats['true'] = transmission * fw_m
        df_stats['pixel'] = df_stats.index
        df_stats.loc[:, ('measured', 'res')]= gb.apply(charge_resolution_df).values
        df_stats.loc[:, ('charge', 'rms')] = gb.apply(rms_charge_df).values
        df_stats.loc[:, ('measured', 'rms')] = gb.apply(rms_measured_df).values

        df_list.append(df_stats)
        reader.store.close()

    df = pd.concat(df_list, ignore_index=True)

    with HDF5Writer(output_path) as writer:
        writer.write(data=df)
        writer.write_mapping(mapping)
        writer.write_metadata(n_pixels=n_pixels)


def main():
    [process(f) for f in all_files]


if __name__ == '__main__':
    main()