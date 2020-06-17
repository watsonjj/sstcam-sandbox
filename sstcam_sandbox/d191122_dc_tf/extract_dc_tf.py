from sstcam_sandbox import get_checs, get_data
from CHECLabPy.core.io import TIOReader
from TargetCalibSB.tf import TFDC
from TargetCalibSB.pedestal import PedestalTargetCalib
from TargetCalibSB import get_cell_ids_for_waveform
from tqdm import tqdm
from glob import glob
import re


def process(tf_r0_paths, pedestal_path, tf_path):
    pedestal = PedestalTargetCalib.from_tcal(pedestal_path)

    # Parse amplitudes from filepath
    amplitudes = []
    readers = []
    for path in tf_r0_paths:
        regex_ped = re.search(r".+_(\d+)_r0.tio", path)
        amplitudes.append(int(regex_ped.group(1)))
        readers.append(TIOReader(path))

    # Instance TF class from first file
    tf = TFDC(
        readers[0].n_pixels,
        readers[0].n_samples - 32,
        readers[0].n_cells,
        amplitudes
    )

    desc0 = "Generating TF"
    it = zip(amplitudes, readers)
    n_amp = len(amplitudes)
    for amplitude, reader in tqdm(it, total=n_amp, desc=desc0):
        amplitude_index = tf.get_input_amplitude_index(amplitude)
        for iwf, wfs in enumerate(reader):
            if wfs.missing_packets:
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
    tf_r0_paths = glob(get_checs("d181203_erlangen/dc_tf/externalsync/23deg/*.tio"))
    pedestal_path = get_checs("d181203_erlangen/pedestal/Pedestal_23deg_ped.tcal")
    tf_path = get_data("d191122_dc_tf/dc_tf/dc_externalsync_23deg_tf.tcal")
    process(tf_r0_paths, pedestal_path, tf_path)

    tf_r0_paths = glob(get_checs("d181203_erlangen/dc_tf/externalsync/40deg/*.tio"))
    pedestal_path = get_checs("d181203_erlangen/pedestal/Pedestal_40deg_ped.tcal")
    tf_path = get_data("d191122_dc_tf/dc_tf/dc_externalsync_40deg_tf.tcal")
    process(tf_r0_paths, pedestal_path, tf_path)

    tf_r0_paths = glob(get_checs("d181203_erlangen/dc_tf/hardsync/23deg/*.tio"))
    pedestal_path = get_checs("d181203_erlangen/pedestal/Pedestal_23deg_ped.tcal")
    tf_path = get_data("d191122_dc_tf/dc_tf/dc_hardsync_23deg_tf.tcal")
    process(tf_r0_paths, pedestal_path, tf_path)

    tf_r0_paths = glob(get_checs("d181203_erlangen/dc_tf/hardsync/40deg/*.tio"))
    pedestal_path = get_checs("d181203_erlangen/pedestal/Pedestal_40deg_ped.tcal")
    tf_path = get_data("d191122_dc_tf/dc_tf/dc_hardsync_40deg_tf.tcal")
    process(tf_r0_paths, pedestal_path, tf_path)


if __name__ == '__main__':
    main()
