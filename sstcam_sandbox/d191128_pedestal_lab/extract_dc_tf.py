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
        regex_ped = re.search(r".+VPED_(\d+).tio", path)
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

            tf.add_to_tf(
                pedestal.subtract_pedestal(wfs, wfs.first_cell_id),
                wfs.first_cell_id,
                amplitude_index
            )

    tf.save(tf_path)


def main():
    # tf_r0_paths = glob("/Users/Jason/Downloads/tempdata/d191128_pedestal_lab/dc_tf_tm_temp25/*.tio")
    # pedestal_path = "/Users/Jason/Downloads/tempdata/d191128_pedestal_lab/dc_tf_tm_temp25/VPED_1095_ped.tcal"
    # tf_path = get_data("d191128_pedestal_lab/dc_tf/before_25deg.h5")
    # process(tf_r0_paths, pedestal_path, tf_path)

    # tf_r0_paths = glob("/Users/Jason/Downloads/tempdata/d191128_pedestal_lab/dc_tf_tm_temp35/*.tio")
    # pedestal_path = "/Users/Jason/Downloads/tempdata/d191128_pedestal_lab/dc_tf_tm_temp25/VPED_1095_ped.tcal"
    # tf_path = get_data("d191128_pedestal_lab/dc_tf/before_35deg.h5")
    # process(tf_r0_paths, pedestal_path, tf_path)

    # tf_r0_paths = glob("/Users/Jason/Downloads/tempdata/d191128_pedestal_lab/dc_tf_tm_temp35_440pF_2/*.tio")
    # pedestal_path = "/Users/Jason/Downloads/tempdata/d191128_pedestal_lab/dc_tf_tm_temp25_440pF/VPED_1095_ped.tcal"
    # tf_path = get_data("d191128_pedestal_lab/dc_tf/after_35deg.h5")
    # process(tf_r0_paths, pedestal_path, tf_path)
    #
    # tf_r0_paths = glob("/Users/Jason/Downloads/tempdata/d191128_pedestal_lab/dc_tf_tm_temp25_440pF/*.tio")
    # pedestal_path = "/Users/Jason/Downloads/tempdata/d191128_pedestal_lab/dc_tf_tm_temp25_440pF/VPED_1095_ped.tcal"
    # tf_path = get_data("d191128_pedestal_lab/dc_tf/after_25deg.h5")
    # process(tf_r0_paths, pedestal_path, tf_path)

    # tf_r0_paths = glob("/Users/Jason/Downloads/tempdata/d191128_pedestal_lab/dc_tf_tm_temp25_440pF_3/*.tio")
    # pedestal_path = "/Users/Jason/Downloads/tempdata/d191128_pedestal_lab/dc_tf_tm_temp25_440pF_3/VPED_1095_ped.tcal"
    # tf_path = get_data("d191128_pedestal_lab/dc_tf/after_25deg_3.h5")
    # process(tf_r0_paths, pedestal_path, tf_path)

    # tf_r0_paths = glob("/Users/Jason/Downloads/tempdata/d191128_pedestal_lab/dc_tf_tm_temp35_440pF_3/*.tio")
    # pedestal_path = "/Users/Jason/Downloads/tempdata/d191128_pedestal_lab/dc_tf_tm_temp25_440pF_3/VPED_1095_ped.tcal"
    # tf_path = get_data("d191128_pedestal_lab/dc_tf/after_35deg_3.h5")
    # process(tf_r0_paths, pedestal_path, tf_path)

    # tf_r0_paths = glob("/Users/Jason/Downloads/tempdata/d191128_pedestal_lab/dc_tf_tm_temp25_100pF/*.tio")
    # pedestal_path = "/Users/Jason/Downloads/tempdata/d191128_pedestal_lab/dc_tf_tm_temp25_100pF/VPED_1095_ped.tcal"
    # tf_path = get_data("d191128_pedestal_lab/dc_tf/100pF_25deg.h5")
    # process(tf_r0_paths, pedestal_path, tf_path)
    #
    # tf_r0_paths = glob("/Users/Jason/Downloads/tempdata/d191128_pedestal_lab/dc_tf_tm_temp35_100pF/*.tio")
    # pedestal_path = "/Users/Jason/Downloads/tempdata/d191128_pedestal_lab/dc_tf_tm_temp25_100pF/VPED_1095_ped.tcal"
    # tf_path = get_data("d191128_pedestal_lab/dc_tf/100pF_35deg.h5")
    # process(tf_r0_paths, pedestal_path, tf_path)

    # tf_r0_paths = glob("/Users/Jason/Downloads/tempdata/d191128_pedestal_lab/dc_tf_tm_temp25_100_pF_1k/*.tio")
    # pedestal_path = "/Users/Jason/Downloads/tempdata/d191128_pedestal_lab/dc_tf_tm_temp25_100pF/VPED_1095_ped.tcal"
    # tf_path = get_data("d191128_pedestal_lab/dc_tf/100pF_1k_25deg.h5")
    # process(tf_r0_paths, pedestal_path, tf_path)

    tf_r0_paths = glob("/Users/Jason/Downloads/tempdata/d191128_pedestal_lab/dc_tf_tm_temp25_200_pF/*.tio")
    pedestal_path = "/Users/Jason/Downloads/tempdata/d191128_pedestal_lab/dc_tf_tm_temp25_200_pF/VPED_1095_ped.tcal"
    tf_path = get_data("d191128_pedestal_lab/dc_tf/200pF_25deg.h5")
    process(tf_r0_paths, pedestal_path, tf_path)

    tf_r0_paths = glob("/Users/Jason/Downloads/tempdata/d191128_pedestal_lab/dc_tf_tm_temp35_200_pF/*.tio")
    pedestal_path = "/Users/Jason/Downloads/tempdata/d191128_pedestal_lab/dc_tf_tm_temp25_200_pF/VPED_1095_ped.tcal"
    tf_path = get_data("d191128_pedestal_lab/dc_tf/200pF_35deg.h5")
    process(tf_r0_paths, pedestal_path, tf_path)

if __name__ == '__main__':
    main()
