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


def process(r0_paths, pedestal, tf, output_path):
    readers = [TIOReader(path) for path in r0_paths]
    df_list = []

    channel = np.arange(readers[0].n_pixels)

    desc0 = "Extracting charges"
    for reader in tqdm(readers, total=len(readers), desc=desc0):
        regex = re.search(r".+Amplitude_([-\d]+)_.+_r0.tio", reader.path)
        amplitude = int(regex.group(1))
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
            charge = wfs[:, 4:21].sum(1)

            df_list.append(pd.DataFrame(dict(
                amplitude=amplitude,
                iev=iev,
                fci=first_cell_id,
                channel=channel,
                charge=charge
            )))

    df = pd.concat(df_list, ignore_index=True)
    with HDF5Writer(output_path) as writer:
        writer.write(data=df)


def main():
    path_ac_23 = get_data("d191122_dc_tf/ac_tf/TFInput_File_SN0038_temp_23_180317.tcal")
    path_ac_cc_23 = get_data("d191122_dc_tf/ac_tf/ac_23deg_tf.h5")
    path_dc_ext23 = get_data("d191122_dc_tf/dc_tf/dc_externalsync_23deg_tf.tcal")
    path_vped_23 = get_data("d191122_dc_tf/vped/VPED_23deg.h5")
    path_pedestal_23 = get_checs("d181203_erlangen/pedestal/Pedestal_23deg_ped.tcal")

    tf_ac_23 = get_ac_tf(path_ac_23)
    tf_ac_cc_23 = get_ac_cc_tf(path_ac_cc_23)
    tf_dc_ext23 = get_dc_tf(path_dc_ext23, path_vped_23)
    pedestal_23 = get_pedestal(path_pedestal_23)

    # r0_paths = glob(get_checs("d181203_erlangen/dynrange/23deg/r0/Amplitude_*_Run_0_r0.tio"))
    # output_path = get_data("d191122_dc_tf/charge/dc_externalsync_23deg_charge.h5")
    # process(r0_paths, pedestal_23, tf_dc_ext23, output_path)
    #
    # r0_paths = glob(get_checs("d181203_erlangen/dynrange/23deg/r0/Amplitude_*_Run_0_r0.tio"))
    # output_path = get_data("d191122_dc_tf/charge/ac_23deg_charge.h5")
    # process(r0_paths, pedestal_23, tf_ac_23, output_path)

    r0_paths = glob(get_checs("d181203_erlangen/dynrange/23deg/r0/Amplitude_*_Run_0_r0.tio"))
    output_path = get_data("d191122_dc_tf/charge/ac_cc_23deg_charge.h5")
    process(r0_paths, pedestal_23, tf_ac_cc_23, output_path)

    # r0_paths = glob(get_checs("d181203_erlangen/dynrange/23deg/r0/Amplitude_*_Run_0_r0.tio"))
    # output_path = get_data("d191122_dc_tf/charge/pedonly_23deg_charge.h5")
    # process(r0_paths, pedestal_23, None, output_path)

if __name__ == '__main__':
    main()
