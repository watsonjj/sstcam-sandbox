from CHECLabPySB import get_data, get_checs
from CHECLabPy.core.io import HDF5Writer
from TargetCalibSB.pedestal import PedestalTargetCalib
from TargetCalibSB.stats import OnlineStats, OnlineHist
from CHECLabPy.core.io import TIOReader
from tqdm import tqdm
import re
import pandas as pd
from glob import glob


class PedestalDB:
    def __init__(self, paths):
        lookup = []
        for path in paths:
            regex_r0 = re.search(r".+_tc([\d.]+)_tmc([\d.]+)_ped.tcal", path)
            temperature_chamber = float(regex_r0.group(1))
            temperature_primary = float(regex_r0.group(2))
            pedestal = PedestalTargetCalib.from_tcal(path)
            lookup.append(dict(
                temperature_chamber=temperature_chamber,
                temperature_primary=temperature_primary,
                pedestal=pedestal,
            ))

        self.lookup = pd.DataFrame(lookup)
        self.lookup = self.lookup.set_index("temperature_primary")

    def get_pedestal(self, temperature):
        loc = self.lookup.index.get_loc(temperature, method='nearest')
        return self.lookup.iloc[loc]['pedestal']


def process(r0_paths, pedestal_paths, output_path):
    pedestal_db = PedestalDB(pedestal_paths)
    data = []

    for ipath, r0_path in enumerate(r0_paths):
        print(f"Processing: {ipath+1}/{len(r0_paths)}")
        regex_r0 = re.search(r".+_tc([\d.]+)_tmc([\d.]+).tio", r0_path)
        temperature_r0_primary = float(regex_r0.group(2))

        pedestal = pedestal_db.get_pedestal(temperature_r0_primary)
        reader = TIOReader(r0_path)

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
            temperature_r0_primary=temperature_r0_primary,
            mean=online_stats.mean,
            std=online_stats.std,
            hist=online_hist.hist,
            edges=online_hist.edges,
        ))

    with HDF5Writer(output_path) as writer:
        writer.write(data=pd.DataFrame(data))


def main():
    # r0_paths = glob(get_checs("d191118_pedestal_temperature/data/d191118/*.tio"))
    # pedestal_paths = glob(get_checs("d191118_pedestal_temperature/lookup/*_ped.tcal"))
    # output_path = get_data(f"d191118_pedestal_temperature/d191118/residuals_lookup.h5")
    # process(r0_paths, pedestal_paths, output_path)

    # r0_paths = glob(get_checs("d191118_pedestal_temperature/data/d191119/*.tio"))
    # pedestal_paths = glob(get_checs("d191118_pedestal_temperature/lookup/*_ped.tcal"))
    # output_path = get_data(f"d191118_pedestal_temperature/d191119/residuals_lookup.h5")
    # process(r0_paths, pedestal_paths, output_path)

    r0_paths = glob(get_checs("d191118_pedestal_temperature/data/d191120/*.tio"))
    pedestal_paths = glob(get_checs("d191118_pedestal_temperature/lookup/*_ped.tcal"))
    output_path = get_data(f"d191118_pedestal_temperature/d191120/residuals_lookup.h5")
    process(r0_paths, pedestal_paths, output_path)


if __name__ == '__main__':
    main()
