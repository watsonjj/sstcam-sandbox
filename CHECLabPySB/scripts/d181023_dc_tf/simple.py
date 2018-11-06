import numpy as np
from matplotlib import pyplot as plt
from CHECLabPy.core.io import TIOReader
from CHECLabPy.utils.files import sort_file_list
from glob import glob
import os
from tqdm import tqdm, trange
from IPython import embed


def read_vped(path):
    with open(path) as f:
        return int(f.readline())


def main():
    # files = glob("/Volumes/gct-jason/data_checs/d181019_dctf/15C/Run*_r0.tio")
    files = glob("/Volumes/gct-jason/data_checs/d181019_dctf/15C/r1_tf/Run*_r1.tio")
    files = sort_file_list(files)
    files = files[1:]
    n_files = len(files)

    mean_p = np.zeros(n_files)
    std_p = np.zeros(n_files)
    mean_s = np.zeros(n_files)
    std_s = np.zeros(n_files)
    vped = np.zeros(n_files)

    for ifile, f in enumerate(files):
        vped_path = f.replace("_r1.tio", "_r0.txt")
        vped[ifile] = read_vped(vped_path)

        r = TIOReader(f)
        n_events = r.n_events
        n_pixels = r.n_pixels
        n_samples = r.n_samples
        samples = np.zeros((n_events, n_pixels, n_samples))
        for iev, wf in enumerate(r):
            samples[iev] = wf

        lookup = samples.mean(0)

        mean_p[ifile] = lookup[:, 0].mean()
        std_p[ifile] = lookup[:, 0].std()
        mean_s[ifile] = lookup[0, :].mean()
        std_s[ifile] = lookup[0, :].std()

    (_, caps, _) = plt.errorbar(vped, mean_p, yerr=std_p, fmt='o', mew=1,
                                markersize=3, capsize=3, elinewidth=0.7, label="")
    for cap in caps:
        cap.set_markeredgewidth(0.7)

    (_, caps, _) = plt.errorbar(vped, mean_s, yerr=std_s, fmt='o', mew=1,
                                markersize=3, capsize=3, elinewidth=0.7, label="")
    for cap in caps:
        cap.set_markeredgewidth(0.7)


    # plt.errorbar(vped, mean_p, yerr=std_p)
    # plt.errorbar(vped, mean_s, yerr=std_s)
    plt.show()

if __name__ == '__main__':
    main()