import os
from CHECLabPySB.scripts.d181123_tf_cell_check import TF_Storage, \
    TF_Sampling, all_files
from CHECLabPy.core.io import TIOReader
import numpy as np
from tqdm import tqdm
from IPython import embed


def process(file, tf):
    r0_path = file.r0_path
    r1_name = os.path.basename(r0_path).replace("_r0", "_r1")
    r1_path = os.path.join(tf.r1_dir, r1_name)
    get_cell = tf.get_cell

    r = TIOReader(r1_path)
    n_events = r.n_events
    n_pixels = r.n_pixels
    n_samples = r.n_samples
    samp_arange = np.arange(n_samples, dtype=np.uint16)
    for wfs in tqdm(r, total=n_events):
        fci = r.first_cell_ids
        cells = get_cell(int(fci[0]), samp_arange)
        cells_pix = np.tile(cells, (n_pixels, 1))
        np.testing.assert_almost_equal(wfs, cells_pix, 1)


def main():
    for f in all_files:
        process(f, TF_Sampling())
        process(f, TF_Storage())


if __name__ == '__main__':
    main()
