from CHECLabPy.core.io import HDF5Appender
from CHECOnsky.astronomy.spectra import get_t_norm_for_events, \
    calculate_t_norm_crab, calculate_t_norm_proton, calculate_weights_crab, \
    calculate_weights_proton
import argparse
import numpy as np
import pandas as pd
from astropy import units as u


def main():
    parser = argparse.ArgumentParser(
        description="Add alpha info to hillas file",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        '-f', '--files', dest='input_paths', nargs='+',
        help='path to the HDF5 hillas files'
    )
    args = parser.parse_args()

    input_paths = args.input_paths

    n_files = len(input_paths)
    for ifile, input_path in enumerate(input_paths):
        print(f"PROGRESS: Processing file {ifile + 1}/{n_files}")

        with HDF5Appender(input_path) as file:
            iobs, iev, shower_primary_id, energies = file.select_columns(
                'mc', ['iobs', 'iev', 'shower_primary_id', 'energy']
            )
            df_mch = file.read('mcheader')

            energies = energies.values * u.TeV
            n_simulated = (df_mch['num_showers'] *
                           df_mch['shower_reuse']).values
            index = df_mch['spectral_index'].values
            e_min = df_mch['energy_range_min'].values * u.TeV
            e_max = df_mch['energy_range_max'].values * u.TeV
            area = (df_mch['max_scatter_range'].values * u.m) ** 2 * np.pi
            solid_angle = (df_mch['max_viewcone_radius'] -
                           df_mch['min_viewcone_radius']).values * u.deg

            event_mcheader = df_mch.set_index('iobs').loc[iobs]
            event_index = event_mcheader['spectral_index'].values

            if (shower_primary_id == 0).all():
                weights = calculate_weights_crab(energies, event_index)
                t_norm = calculate_t_norm_crab(
                    e_min, e_max, area, solid_angle, index, n_simulated
                )
            elif (shower_primary_id == 101).all():
                weights = calculate_weights_proton(energies, event_index)
                t_norm = calculate_t_norm_proton(
                    e_min, e_max, area, solid_angle, index, n_simulated
                )
            elif (shower_primary_id != shower_primary_id[0]).all():
                raise ValueError("Mixed shower_primary_id in file")
            else:
                raise ValueError("Unknown shower_primary_id")

            t_norm_events = get_t_norm_for_events(
                energies, e_min, e_max, t_norm
            )

            file.write(weights=pd.DataFrame(dict(
                iobs=iobs.values,
                iev=iev.values,
                weights=weights,
                t_norm=t_norm_events,
            )))


if __name__ == '__main__':
    main()
