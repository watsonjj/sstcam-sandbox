from CHECLabPySB import get_checs
from TargetCalibSB.pedestal import PedestalTargetCalib
from CHECLabPy.core.io import TIOReader
from tqdm import tqdm
from glob import glob


def process(input_paths):
    for path in input_paths:
        pedestal_path = path.replace(".tio", "_ped.tcal")
        reader = TIOReader(path)

        pedestal = PedestalTargetCalib(
            reader.n_pixels, reader.n_samples, reader.n_cells
        )
        desc = "Generating pedestal"
        for wfs in tqdm(reader, total=reader.n_events, desc=desc):
            if wfs.missing_packets:
                continue
            pedestal.add_to_pedestal(wfs, wfs.first_cell_id)
        pedestal.save_tcal(pedestal_path)


def main():
    # input_paths = glob("/Users/Jason/Downloads/tempdata/d191128_pedestal_lab/dc_tf_tm_temp25/*.tio")
    # process(input_paths)

    # input_paths = glob("/Users/Jason/Downloads/tempdata/d191128_pedestal_lab/dc_tf_tm_temp35/*.tio")
    # process(input_paths)

    # input_paths = glob("/Users/Jason/Downloads/tempdata/d191128_pedestal_lab/dc_tf_tm_temp35_440pF_2/*.tio")
    # process(input_paths)

    # input_paths = glob("/Users/Jason/Downloads/tempdata/d191128_pedestal_lab/dc_tf_tm_temp25_440pF/*.tio")
    # process(input_paths)

    # input_paths = glob("/Users/Jason/Downloads/tempdata/d191128_pedestal_lab/dc_tf_tm_temp25_440pF_3/*.tio")
    # process(input_paths)

    # input_paths = glob("/Users/Jason/Downloads/tempdata/d191128_pedestal_lab/dc_tf_tm_temp35_440pF_3/*.tio")
    # process(input_paths)

    # input_paths = glob("/Users/Jason/Downloads/tempdata/d191128_pedestal_lab/dc_tf_tm_temp25_100pF/*.tio")
    # process(input_paths)

    # input_paths = glob("/Users/Jason/Downloads/tempdata/d191128_pedestal_lab/dc_tf_tm_temp35_100pF/*.tio")
    # process(input_paths)

    # input_paths = glob("/Users/Jason/Downloads/tempdata/d191128_pedestal_lab/dc_tf_tm_temp25_100_pF_1k/*.tio")
    # process(input_paths)
    #
    # input_paths = glob("/Users/Jason/Downloads/tempdata/d191128_pedestal_lab/dc_tf_tm_temp25_100_2pF/*.tio")
    # process(input_paths)

    # input_paths = glob("/Users/Jason/Downloads/tempdata/d191128_pedestal_lab/dc_tf_tm_temp25_200_pF/*.tio")
    # process(input_paths)

    input_paths = glob("/Users/Jason/Downloads/tempdata/d191128_pedestal_lab/dc_tf_tm_temp35_200_pF/*.tio")
    process(input_paths)


if __name__ == '__main__':
    main()
