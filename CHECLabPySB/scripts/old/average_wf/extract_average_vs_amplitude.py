import argparse
import os
from argparse import ArgumentDefaultsHelpFormatter as Formatter
import numpy as np
from tqdm import tqdm
from CHECLabPy.utils.waveform import get_average_wf
from CHECLabPy.utils.files import open_runlist_r1


def main():
    description = 'Extract the average wf across the camera per illumination'
    parser = argparse.ArgumentParser(description=description,
                                     formatter_class=Formatter)
    parser.add_argument('-f', '--file', dest='input_path',
                        action='store', required=True,
                        help='path to the runlist txt file')
    parser.add_argument('-n', '--maxevents', dest='max_events', action='store',
                        help='Number of events to process', type=int)
    parser.add_argument('-o', '--output', dest='output_path',
                        action='store', required=True,
                        help='path to store the output HDFStore file')
    args = parser.parse_args()

    runlist = args.input_path
    max_events = args.max_events
    output_path = args.output_path

    df_runs = open_runlist_r1(runlist, max_events=max_events)

    if os.path.exists(output_path):
        os.remove(output_path)

    t_shift = 60
    average_wf_dict = dict()
    desc = "Looping over files"
    n_rows = df_runs.index.size
    for index, row in tqdm(df_runs.iterrows(), total=n_rows, desc=desc):
        reader = row['reader']
        illumination = row['illumination']

        average_wf = get_average_wf(reader, t_shift)
        average_wf_dict["{:.3f}".format(illumination)] = average_wf

    np.savez(output_path, **average_wf_dict)


if __name__ == '__main__':
    main()
