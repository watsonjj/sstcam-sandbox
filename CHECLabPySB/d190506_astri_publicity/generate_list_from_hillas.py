import argparse
from argparse import ArgumentDefaultsHelpFormatter as Formatter
from CHECLabPy.core.io import HDF5Reader
from CHECLabPy.utils.files import create_directory
from os.path import dirname
import numpy as np
import pandas as pd


def main():
    description = 'Loop over R0 or R1 file and plot camera images'
    parser = argparse.ArgumentParser(description=description,
                                     formatter_class=Formatter)
    parser.add_argument('-f', '--files', dest='input_paths', nargs='+',
                        help='path to the hillas files containing waveforms')
    parser.add_argument('-o', '--output', dest='output_path', required=True,
                        help='Path to save output file')
    parser.add_argument('-n', '--maxevents', dest='max_events', type=int,
                        help='Maximum number of events to process')
    parser.add_argument('--random', dest='random', action='store_true',
                        help='Randomise order of events')
    parser.add_argument('--cuts', dest='cuts',
                        help='Cuts to apply to the hillas parameters, '
                             'specified as a string. E.g.: '
                             '--cuts "intensity > 200 and width < 0.5"')
    args = parser.parse_args()

    input_paths = args.input_paths
    output_path = args.output_path
    max_events = args.max_events
    random = args.random
    cuts = args.cuts

    df_list = []

    for path in input_paths:
        with HDF5Reader(path) as reader:
            df = reader.select('data', where=cuts)

            df_list.append(pd.DataFrame(dict(
                path=path,
                iobs=df['iobs'].values,
                iev=df['iev'].values,
                intensity=df['intensity'].values,
                width=df['width'].values,
                length=df['length'].values,
                tgradient=df['tgradient'].values,
            )))

    df = pd.concat(df_list, ignore_index=True, sort=False)
    index = df.index.values
    if random:
        np.random.shuffle(index)
    if max_events is not None:
        index = index[:max_events]
    df = df.iloc[index]

    create_directory(dirname(output_path))
    df.to_csv(output_path, sep='\t', index=False, float_format="%.4f")
    print(f"Created file with {df.index.size} events: {output_path}")


if __name__ == '__main__':
    main()
