from CHECLabPySB import get_checs, get_data
from TargetCalibSB.pedestal import PedestalTargetCalib
from CHECLabPy.core.io import HDF5Writer
from CHECLabPy.utils.files import sort_file_list
import pandas as pd
from glob import glob
import re


def process(pedestal_paths, output_path):
    pedestal_paths = sort_file_list(pedestal_paths)

    data = []
    reference_values = None
    reference_spread = None

    for path in pedestal_paths:
        regex_ped = re.search(r".+_tc([\d.]+)_tmc([\d.]+)_ped.tcal", path)
        temperature_pedestal_primary = float(regex_ped.group(2))

        pedestal = PedestalTargetCalib.from_tcal(path)
        values = pedestal.pedestal
        spread = pedestal.std

        if reference_values is None:
            reference_values = values
            reference_spread = spread

        delta = values - reference_values
        delta_mean = delta.mean()
        delta_std = delta.std()
        delta_channel_mean = delta[0].mean()
        delta_channel_std = delta[0].std()

        # delta_spread = spread - reference_spread
        spread_mean = spread.mean()
        spread_std = spread.std()

        data.append(dict(
            temperature=temperature_pedestal_primary,
            delta_mean=delta_mean,
            delta_std=delta_std,
            delta_channel_mean=delta_channel_mean,
            delta_channel_std=delta_channel_std,
            spread_mean=spread_mean,
            spread_std=spread_std,
        ))

    with HDF5Writer(output_path) as writer:
        writer.write(data=pd.DataFrame(data))


def main():
    pedestal_paths = glob(get_checs("d191118_pedestal_temperature/data/d191118/*_ped.tcal"))
    output_path = get_data(f"d191118_pedestal_temperature/d191118/adc_vs_temperature.h5")
    process(pedestal_paths, output_path)

    pedestal_paths = glob(get_checs("d191118_pedestal_temperature/data/d191119/*_ped.tcal"))
    output_path = get_data(f"d191118_pedestal_temperature/d191119/adc_vs_temperature.h5")
    process(pedestal_paths, output_path)

    pedestal_paths = glob(get_checs("d191118_pedestal_temperature/data/d191120/*_ped.tcal"))
    output_path = get_data(f"d191118_pedestal_temperature/d191120/adc_vs_temperature.h5")
    process(pedestal_paths, output_path)


if __name__ == '__main__':
    main()
