import argparse
from argparse import ArgumentDefaultsHelpFormatter as Formatter
import os
import pandas as pd
from tqdm import tqdm
from CHECLabPy.utils.files import open_runlist_dl1


def main():
    description = 'Create a new HDFStore file containing the time corrections'
    parser = argparse.ArgumentParser(description=description,
                                     formatter_class=Formatter)
    parser.add_argument('-f', '--file', dest='input_path',
                        action='store', required=True,
                        help='path to the runlist txt file')
    parser.add_argument('-o', '--output', dest='output_path',
                        action='store', required=True,
                        help='path to store the output HDFStore file')
    args = parser.parse_args()

    input_path = args.input_path
    output_path = args.output_path

    df_runs = open_runlist_dl1(input_path)

    if os.path.exists(output_path):
        os.remove(output_path)

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
