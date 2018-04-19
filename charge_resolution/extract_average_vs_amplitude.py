import argparse
import os
import re
from argparse import ArgumentDefaultsHelpFormatter as Formatter
import numpy as np
from tqdm import tqdm
from CHECLabPy.core.io import ReaderR1
from CHECLabPy.utils.waveform import get_average_wf


def commonsuffix(files):
    reveresed = [f[::-1] for f in files]
    return os.path.commonprefix(reveresed)[::-1]


def obtain_amplitude_from_filename(files):
    commonprefix = os.path.commonprefix
    pattern = commonprefix(files) + '(.+?)' + commonsuffix(files)
    amplitudes = []
    for fp in files:
        try:
            reg_exp = re.search(pattern, fp)
            if reg_exp:
                amplitudes.append(reg_exp.group(1))
        except AttributeError:
            print("Problem with Regular Expression, "
                  "{} does not match patten {}".format(fp, pattern))
    return amplitudes


def obtain_readers(files, max_events):
    return [ReaderR1(fp, max_events) for fp in files]


def main():
    description = ''
    parser = argparse.ArgumentParser(description=description,
                                     formatter_class=Formatter)
    parser.add_argument('-f', '--files', dest='input_paths',
                        nargs='+', help='paths to the input dl1 HDF5 files')
    parser.add_argument('-n', '--maxevents', dest='max_events', action='store',
                        help='Number of events to process', type=int)
    parser.add_argument('-o', '--output', dest='output_path',
                        action='store', required=True,
                        help='path to store the output HDFStore file')
    args = parser.parse_args()

    files = args.input_paths
    max_events = args.max_events
    output_path = args.output_path

    readers = obtain_readers(files, max_events)
    amplitudes = obtain_amplitude_from_filename(files)

    assert len(readers) == len(amplitudes)

    if os.path.exists(output_path):
        os.remove(output_path)

    t_shift = 35
    average_wf_dict = dict()
    desc = "Looping over files"
    iter_z = zip(readers, amplitudes)
    for r, amp in tqdm(iter_z, total=len(readers), desc=desc):
        average_wf = get_average_wf(r, t_shift)
        average_wf_dict[amp] = average_wf

    np.savez(output_path, **average_wf_dict)


if __name__ == '__main__':
    main()
