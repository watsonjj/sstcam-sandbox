import argparse
from argparse import ArgumentDefaultsHelpFormatter as Formatter
import re
import numpy as np
import pandas as pd


def extract_hv_cfg(path):
    pattern_dac = re.compile(r"M:(\d+)/F/S:(\d+)\|HV=(\d+)")
    pattern_hvon = re.compile(r"M:(\d+)/F/S:(\d+)\|HVOn=(\d+)")

    dac = np.zeros((32, 16), dtype=np.int16)
    hvon = np.zeros((32, 16), dtype=np.int16)

    with open(path) as file:
        for line in file:
            if 'HVOn' in line:
                pattern = pattern_hvon
                value_array = hvon
            else:
                pattern = pattern_dac
                value_array = dac
            reg_exp = re.search(pattern, line)
            if reg_exp:
                tm = int(reg_exp.group(1))
                sp = int(reg_exp.group(2))
                value_array[tm, sp] = int(reg_exp.group(3))
    return dac, hvon


def main():
    description = 'Convert HV cfg file to csv'
    parser = argparse.ArgumentParser(description=description,
                                     formatter_class=Formatter)
    parser.add_argument('-f', '--file', dest='input_path', action='store',
                        help='path to the HV cfg file')
    parser.add_argument('-o', '--output', dest='output_path', action='store',
                        help='path to store the output csv file')
    args = parser.parse_args()

    input_path = args.input_path
    output_path = args.output_path

    dac, hvon = extract_hv_cfg(input_path)

    tm, sp = np.indices(dac.shape)

    df = pd.DataFrame(dict(
        tm=tm.ravel(),
        superpixel=sp.ravel(),
        dac=dac.ravel(),
        hvon=hvon.ravel(),
    ))
    df.to_csv(output_path, sep='\t', index=False)


if __name__ == '__main__':
    main()
