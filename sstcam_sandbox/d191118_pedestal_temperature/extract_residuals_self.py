from sstcam_sandbox import get_data, get_checs
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

        regex_r0 = re.search(r".+_tc([\d.]+)_tmc([\d.]+).tio", r0_path)
        temperature_r0_chamber = float(regex_r0.group(1))
        temperature_r0_primary = float(regex_r0.group(2))

        regex_ped = re.search(r".+_tc([\d.]+)_tmc([\d.]+)_ped.tcal", pedestal_path)
        temperature_pedestal_chamber = float(regex_ped.group(1))
        temperature_pedestal_primary = float(regex_ped.group(2))

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

            subtracted_tc = pedestal.subtract_pedestal(wfs, wfs.first_cell_id)[[0]]
            online_stats.add_to_stats(subtracted_tc)
            online_hist.add(subtracted_tc)

        data.append(dict(
            temperature_r0_chamber=temperature_r0_chamber,
            temperature_r0_primary=temperature_r0_primary,
            temperature_pedestal_chamber=temperature_pedestal_chamber,
            temperature_pedestal_primary=temperature_pedestal_primary,
            mean=online_stats.mean,
            std=online_stats.std,
            hist=online_hist.hist,
            edges=online_hist.edges,
        ))

    with HDF5Writer(output_path) as writer:
        writer.write(data=pd.DataFrame(data))


def main():
    r0_paths = glob(get_checs("d191118_pedestal_temperature/data/d191118/*.tio"))
    output_dir = get_data(f"d191118_pedestal_temperature/d191118/residuals_self.h5")
    process(r0_paths, output_dir)


if __name__ == '__main__':
    main()
