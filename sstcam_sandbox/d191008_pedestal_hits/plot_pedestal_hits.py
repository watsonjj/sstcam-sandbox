import argparse
from argparse import ArgumentDefaultsHelpFormatter as Formatter
from CHECLabPy.core.io import TIOReader
from os.path import exists, join
from os import makedirs
import numpy as np
from numba import njit, prange
from matplotlib import pyplot as plt
from tqdm import tqdm
from astropy.utils.console import color_print

N_BLOCKPHASE = 32


@njit(fastmath=True, parallel=True)
def welfords_online_algorithm(sample, mean, count, m2):
    delta = sample - mean
    count += 1
    mean += delta / count
    delta2 = sample - mean
    m2 += delta * delta2
    return mean, count, m2


class Pedestal:
    def __init__(self, n_pixels, n_samples, n_cells):
        n_blocks = n_cells // N_BLOCKPHASE
        n_bpisam = N_BLOCKPHASE + n_samples - 1
        shape = (n_pixels, n_blocks, n_bpisam)
        self._pedestal = np.zeros(shape, dtype=np.float32)
        self._hits = np.zeros(shape, dtype=np.uint32)
        self._m2 = np.zeros(shape, dtype=np.float32)

    def add_to_pedestal(self, wfs, fci):
        self._add_to_pedestal(wfs, fci, self._pedestal, self._hits, self._m2)

    @staticmethod
    @njit(fastmath=True, parallel=True)
    def _add_to_pedestal(wfs, fci, pedestal, hits, m2):
        fblockphase = fci % 32
        fblock = fci // 32

        n_pixels, n_samples = wfs.shape
        for ipix in prange(n_pixels):
            for isam in prange(n_samples):
                sample = wfs[ipix, isam]
                fbpisam = fblockphase + isam
                idx = (ipix, fblock, fbpisam)
                pedestal[idx], hits[idx], m2[idx] = welfords_online_algorithm(
                    sample, pedestal[idx], hits[idx], m2[idx]
                )

    @property
    def pedestal(self):
        return self._pedestal

    @property
    def hits(self):
        return self._hits

    @property
    def variance(self):
        return self._m2 / (self._hits - 1)

    @property
    def std(self):
        return np.sqrt(self.variance)


def plot_2d(data, clabel, output_path):
    fig = plt.figure(figsize=(6, 4))
    ax = fig.add_subplot(1, 1, 1)

    pixel_hits_0 = np.ma.masked_where(data == 0, data)

    im = ax.pcolor(pixel_hits_0,
                   cmap="viridis", edgecolors='white', linewidths=0.1)
    cbar = fig.colorbar(im)
    ax.patch.set(hatch='xx')
    ax.set_xlabel("Blockphase + Waveform position")
    ax.set_ylabel("Block")
    cbar.set_label(clabel)
    fig.savefig(output_path, bbox_inches='tight')
    print("Figure saved to: {}".format(output_path))


def print_check(success, msg):
    symbol = '\u2713' if success else '\u274c'
    color_print(f"CHECK: {msg} ", 'yellow', symbol, 'green')


def main():
    description = 'Plot the properties of the pedestal from an R0 file'
    parser = argparse.ArgumentParser(description=description,
                                     formatter_class=Formatter)
    parser.add_argument('-f', '--file', dest='input_path', required=True,
                        help='path to the TIO file')
    parser.add_argument('-o', '--output', dest='output_dir', action='store',
                        help='directory to store plots')
    parser.add_argument('-n', '--maxevents', dest='max_events', action='store',
                        help='Number of events to process', type=int)
    args = parser.parse_args()

    input_path = args.input_path
    output_dir = args.output_dir
    max_events = args.max_events

    if not exists(output_dir):
        print("Creating directory: {}".format(output_dir))
        makedirs(output_dir)

    reader = TIOReader(input_path, max_events=max_events)
    pedestal = Pedestal(reader.n_pixels, reader.n_samples, reader.n_cells)
    pixel = 0

    # Generate pedestal
    for wfs in tqdm(reader, total=reader.n_events, desc="Generating Pedestal"):
        pedestal.add_to_pedestal(wfs, wfs.first_cell_id)

    max_expected = 1.7
    mean_std = pedestal.std.mean()
    print_check(
        mean_std < max_expected,
        f"Average pedestal stddev: {mean_std:.2f} ADC "
        f"(max expected: ~{max_expected} ADC)"
    )

    pedestal_pix = pedestal.pedestal[pixel]
    plot_2d(pedestal_pix, "Average ADC", join(output_dir, "pedestal.pdf"))

    hits_pix = pedestal.hits[pixel]
    plot_2d(hits_pix, "Hits", join(output_dir, "hits.pdf"))

    std_pix = pedestal.std[pixel]
    plot_2d(std_pix, "StdDev", join(output_dir, "std.pdf"))


if __name__ == '__main__':
    main()
