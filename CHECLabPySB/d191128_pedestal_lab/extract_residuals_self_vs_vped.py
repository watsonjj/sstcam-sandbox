from CHECLabPySB import get_data, get_checs
from CHECLabPy.core.io import HDF5Writer
from TargetCalibSB.pedestal import PedestalTargetCalib
from TargetCalibSB.stats import OnlineStats, OnlineHist
from CHECLabPy.core.io import TIOReader
from tqdm import tqdm
import re
import pandas as pd
from glob import glob


def process(r0_paths, output_path):
    data = []

    for ipath, r0_path in enumerate(r0_paths):
        print(f"Processing: {ipath+1}/{len(r0_paths)}")
        pedestal_path = r0_path.replace(".tio", "_ped.tcal")

        regex_r0 = re.search(r".+VPED_(\d+).tio", r0_path)
        vped = float(regex_r0.group(1))

        reader = TIOReader(r0_path, max_events=50000)
        pedestal = PedestalTargetCalib(
            reader.n_pixels, reader.n_samples, reader.n_cells
        )
        pedestal.load_tcal(pedestal_path)

        online_stats = OnlineStats()
        online_hist = OnlineHist(bins=100, range_=(-10, 10))

        # Subtract Pedestals
        desc = "Subtracting pedestal"
        for wfs in tqdm(reader, total=reader.n_events, desc=desc):
            if wfs.missing_packets:
                continue

            subtracted_tc = pedestal.subtract_pedestal(wfs, wfs.first_cell_id)[:32]
            online_stats.add_to_stats(subtracted_tc)
            online_hist.add(subtracted_tc)

        data.append(dict(
            vped=vped,
            mean=online_stats.mean,
            std=online_stats.std,
            hist=online_hist.hist,
            edges=online_hist.edges,
        ))

    with HDF5Writer(output_path) as writer:
        writer.write(data=pd.DataFrame(data))


def main():
    # r0_paths = glob("/Users/Jason/Downloads/tempdata/d191128_pedestal_lab/dc_tf_tm_temp25/*.tio")
    # output_path = get_data("d191128_pedestal_lab/residuals_self_vs_vped/before_25deg.h5")
    # process(r0_paths, output_path)
    #
    # r0_paths = glob("/Users/Jason/Downloads/tempdata/d191128_pedestal_lab/dc_tf_tm_temp35/*.tio")
    # output_path = get_data("d191128_pedestal_lab/residuals_self_vs_vped/before_35deg.h5")
    # process(r0_paths, output_path)
    #
    # r0_paths = glob("/Users/Jason/Downloads/tempdata/d191128_pedestal_lab/dc_tf_tm_temp35_440pF_2/*.tio")
    # output_path = get_data("d191128_pedestal_lab/residuals_self_vs_vped/after_35deg.h5")
    # process(r0_paths, output_path)

    # r0_paths = glob("/Users/Jason/Downloads/tempdata/d191128_pedestal_lab/dc_tf_tm_temp25_440pF/*.tio")
    # output_path = get_data("d191128_pedestal_lab/residuals_self_vs_vped/after_25deg.h5")
    # process(r0_paths, output_path)

    # r0_paths = glob("/Users/Jason/Downloads/tempdata/d191128_pedestal_lab/dc_tf_tm_temp25_440pF_3/*.tio")
    # output_path = get_data("d191128_pedestal_lab/residuals_self_vs_vped/after_25deg_3.h5")
    # process(r0_paths, output_path)
    #
    # r0_paths = glob("/Users/Jason/Downloads/tempdata/d191128_pedestal_lab/dc_tf_tm_temp35_440pF_3/*.tio")
    # output_path = get_data("d191128_pedestal_lab/residuals_self_vs_vped/after_35deg_3.h5")
    # process(r0_paths, output_path)

    # r0_paths = glob("/Users/Jason/Downloads/tempdata/d191128_pedestal_lab/dc_tf_tm_temp25_100pF/*.tio")
    # output_path = get_data("d191128_pedestal_lab/residuals_self_vs_vped/100pF_25deg.h5")
    # process(r0_paths, output_path)

    # r0_paths = glob("/Users/Jason/Downloads/tempdata/d191128_pedestal_lab/dc_tf_tm_temp35_100pF/*.tio")
    # output_path = get_data("d191128_pedestal_lab/residuals_self_vs_vped/100pF_35deg.h5")
    # process(r0_paths, output_path)

    r0_paths = glob("/Users/Jason/Downloads/tempdata/d191128_pedestal_lab/dc_tf_tm_temp25_100_pF_1k/*.tio")
    output_path = get_data("d191128_pedestal_lab/residuals_self_vs_vped/100pF_1k_25deg.h5")
    process(r0_paths, output_path)

    # r0_paths = glob("/Users/Jason/Downloads/tempdata/d191128_pedestal_lab/dc_tf_tm_temp25_200_pF/*.tio")
    # output_path = get_data("d191128_pedestal_lab/residuals_self_vs_vped/200pF_25deg.h5")
    # process(r0_paths, output_path)


if __name__ == '__main__':
    main()
