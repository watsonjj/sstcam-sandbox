from sstcam_sandbox import get_checs, get_data
from CHECLabPy.core.io import TIOReader
from TargetCalibSB.tf import TFDC, TFACCrossCorrelation
from TargetCalibSB.pedestal import PedestalTargetCalib
from TargetCalibSB import get_cell_ids_for_waveform
from tqdm import tqdm
from glob import glob
import numpy as np
import re


def process(tf_r0_paths, pedestal_path, tf_path, tf_class):
    pedestal = PedestalTargetCalib.from_tcal(pedestal_path)

    # Parse amplitudes from filepath
    amplitudes = []
    readers = []
    for path in tf_r0_paths:
        regex_ped = re.search(r".+_(-?\d+)_r0.tio", path)
        amplitudes.append(int(regex_ped.group(1)))
        readers.append(TIOReader(path))

    # Instance TF class from first file
    tf = tf_class(
        readers[0].n_pixels,
        readers[0].n_samples - 32,
        readers[0].n_cells,
        amplitudes
    )
    if tf_class == TFACCrossCorrelation:
        # # Estimate range of peak positions
        # r = readers[np.abs(np.array(amplitudes) - 500).argmin()]
        # peak = r[0].mean(0).argmax()
        # tf.set_trange(peak - 5 - 32, peak + 5 - 32)
        tf.set_trange(6, 16)

    desc0 = "Generating TF"
    it = zip(amplitudes, readers)
    n_amp = len(amplitudes)
    for amplitude, reader in tqdm(it, total=n_amp, desc=desc0):
        amplitude_index = tf.get_input_amplitude_index(amplitude)
        for iwf, wfs in enumerate(tqdm(reader, total=reader.n_events)):
            if wfs.missing_packets:
                print("Skipping event")
                continue

            # Skip to next file when enough hits are reached
            if iwf % 1000 == 0:
                if (tf.hits[..., amplitude_index] > 100).all():
                    break

            cells = get_cell_ids_for_waveform(
                wfs.first_cell_id, reader.n_samples, reader.n_cells
            )
            wfs = wfs[:, 32:]
            wfs.first_cell_id = cells[32]
            tf.add_to_tf(
                pedestal.subtract_pedestal(wfs, wfs.first_cell_id),
                wfs.first_cell_id,
                amplitude_index
            )

    tf.save(tf_path)


def main():
    # tf_r0_paths = glob(get_checs("d181203_erlangen/dc_tf/externalsync/23deg/*.tio"))
    # pedestal_path = get_checs("d181203_erlangen/pedestal/Pedestal_23deg_ped.tcal")
    # tf_path = get_data("d191122_dc_tf/dc_tf/dc_externalsync_23deg_tf.tcal")
    # tf_class = TFDC
    # process(tf_r0_paths, pedestal_path, tf_path, tf_class)
    #
    # tf_r0_paths = glob(get_checs("d181203_erlangen/dc_tf/externalsync/40deg/*.tio"))
    # pedestal_path = get_checs("d181203_erlangen/pedestal/Pedestal_40deg_ped.tcal")
    # tf_path = get_data("d191122_dc_tf/dc_tf/dc_externalsync_40deg_tf.tcal")
    # tf_class = TFDC
    # process(tf_r0_paths, pedestal_path, tf_path, tf_class)
    #
    # tf_r0_paths = glob(get_checs("d181203_erlangen/dc_tf/hardsync/23deg/*.tio"))
    # pedestal_path = get_checs("d181203_erlangen/pedestal/Pedestal_23deg_ped.tcal")
    # tf_path = get_data("d191122_dc_tf/dc_tf/dc_hardsync_23deg_tf.tcal")
    # tf_class = TFDC
    # process(tf_r0_paths, pedestal_path, tf_path, tf_class)
    #
    # tf_r0_paths = glob(get_checs("d181203_erlangen/dc_tf/hardsync/40deg/*.tio"))
    # pedestal_path = get_checs("d181203_erlangen/pedestal/Pedestal_40deg_ped.tcal")
    # tf_path = get_data("d191122_dc_tf/dc_tf/dc_hardsync_40deg_tf.tcal")
    # tf_class = TFDC
    # process(tf_r0_paths, pedestal_path, tf_path, tf_class)

    tf_r0_paths = glob(get_checs("d181203_erlangen/ac_tf/23deg/Amplitude_*.tio"))
    pedestal_path = get_checs("d181203_erlangen/pedestal/Pedestal_23deg_ped.tcal")
    tf_path = get_data("d191122_dc_tf/ac_tf/ac_23deg_tf.h5")
    tf_class = TFACCrossCorrelation
    process(tf_r0_paths, pedestal_path, tf_path, tf_class)

    # tf_r0_paths = glob(get_checs("d181203_erlangen/ac_tf/40deg/*.tio"))
    # pedestal_path = get_checs("d181203_erlangen/pedestal/Pedestal_40deg_ped.tcal")
    # tf_path = get_data("d191122_dc_tf/ac_tf/ac_40deg_tf.h5")
    # tf_class = TFACCrossCorrelation
    # process(tf_r0_paths, pedestal_path, tf_path, tf_class)


if __name__ == '__main__':
    main()
