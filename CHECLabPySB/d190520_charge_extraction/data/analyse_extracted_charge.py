from CHECLabPy.core.io import HDF5Reader, HDF5Writer
from CHECLabPySB import get_data
from os.path import dirname, abspath
import numpy as np
import pandas as pd
from IPython import embed


DIR = abspath(dirname(__file__))


def process(path, output):
    with HDF5Reader(path) as reader:
        df = reader.read("data")

    d_list = []

    for extractor, group in df.groupby("extractor"):
        params = dict(extractor=extractor)
        for key, group_key in group.groupby("key"):
            charge = group_key['charge'].values
            params[f'mean_{key}'] = np.mean(charge)
            params[f'std_{key}'] = np.std(charge)
        d_list.append(params)

    df_output = pd.DataFrame(d_list)
    df_output['sn_on_50'] = df_output['mean_on_50'] / df_output['std_off']
    df_output['sn_on_3'] = df_output['mean_on_3'] / df_output['std_off']

    with HDF5Writer(output) as writer:
        writer.write(data=df_output)


def main():
    path = get_data("d190520_charge_extraction/data/charge.h5")
    output = get_data("d190520_charge_extraction/data/analysis.h5")
    process(path, output)


if __name__ == '__main__':
    main()
