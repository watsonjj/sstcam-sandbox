import argparse
from argparse import ArgumentDefaultsHelpFormatter as Formatter
import pandas as pd


def main():
    description = 'Loop over R0 or R1 file and plot camera images'
    parser = argparse.ArgumentParser(description=description,
                                     formatter_class=Formatter)
    parser.add_argument('-f', '--files', dest='input_paths', nargs='+',
                        help='paths to hillas files')
    args = parser.parse_args()

    input_paths = args.input_paths

    for path in input_paths:
        output = path.replace(".h5", ".csv")
        df = pd.HDFStore(path, mode='r')['data']
        df.to_csv(output, index=False)
        print(f"Created csv: {output}")


if __name__ == '__main__':
    main()
