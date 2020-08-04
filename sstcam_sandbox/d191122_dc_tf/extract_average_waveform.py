from sstcam_sandbox import get_checs, get_data
from sstcam_sandbox.d191122_dc_tf import get_dc_tf, get_ac_tf, get_ac_cc_tf
from CHECLabPy.core.io import TIOReader
from CHECLabPy.core.io import HDF5Writer
from TargetCalibSB import correct_overflow
from TargetCalibSB.pedestal import PedestalTargetCalib
from TargetCalibSB import get_cell_ids_for_waveform
import numpy as np
import pandas as pd
from tqdm import tqdm
from glob import glob
from numba import njit, prange
import re
from matplotlib import pyplot as plt
from IPython import embed


def get_pedestal(pedestal_path):
    return PedestalTargetCalib.from_tcal(pedestal_path)


@njit
def extract_charge(waveforms):
    n_pixels, n_samples = waveforms.shape
    start = 4
    end = 20
    charge = np.zeros(n_pixels, dtype=np.float32)
    for ipix in prange(n_pixels):
        for isample in prange(start, end):
            if 0 <= isample < n_samples:
                charge[ipix] += waveforms[ipix, isample]


def process(r0_path, pedestal, tf, output_path):
    reader = TIOReader(r0_path, max_events=1000)
    sum = np.zeros(reader.n_samples-32)
    n = 0

    for wfs in tqdm(reader, total=reader.n_events):
        if wfs.missing_packets:
            continue
        cells = get_cell_ids_for_waveform(
            wfs.first_cell_id, reader.n_samples, reader.n_cells
        )
        wfs = wfs[:, 32:]
        wfs.first_cell_id = cells[32]

        iev = wfs.iev
        first_cell_id = wfs.first_cell_id
        wfs = correct_overflow(wfs)
        wfs = pedestal.subtract_pedestal(wfs, first_cell_id)
        if tf is not None:
            wfs = tf.apply_tf(wfs, first_cell_id)

        if np.isnan(wfs).any():
            continue

        sum += wfs.sum(0)
        n += wfs.shape[0]

    avg = sum / n
    avg /= avg.max()
    array = np.column_stack([np.arange(avg.size)*1e-9, avg]).astype(np.float32)
    print(f"Creating file: {output_path}")
    np.savetxt(output_path, array)


def main():
    r0_path = get_checs("d181203_erlangen/ac_tf/23deg/Amplitude_600_r0.tio")
    pedestal_path = get_checs("d181203_erlangen/pedestal/Pedestal_23deg_ped.tcal")
    tf_path = get_data("d191122_dc_tf/ac_tf/ac_23deg_tf.h5")

    pedestal = get_pedestal(pedestal_path)
    tf = get_ac_cc_tf(tf_path)

    output_path = get_data("d191122_dc_tf/average_wf.txt")
    process(r0_path, pedestal, tf, output_path)


if __name__ == '__main__':
    main()
