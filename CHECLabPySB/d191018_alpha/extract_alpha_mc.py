from CHECLabPy.core.io import HDF5Reader, HDF5Writer
from CHECOnsky.astri import LOCATION
from CHECOnsky.scripts_pipeline.add_alpha import calculate_alpha
from CHECOnsky.astronomy.frames import EngineeringCameraFrame
from CHECOnsky.astronomy.frames import get_telescope_pointing, \
    get_engineering_frame, rotate_about_camera_centre
from CHECOnsky.astronomy.spectra import get_t_norm_for_events, \
    calculate_t_norm_crab, calculate_t_norm_proton, calculate_weights_crab, \
    calculate_weights_proton
from CHECLabPySB import get_data, get_astri_2019
import numpy as np
import pandas as pd
from astropy.coordinates import SkyCoord, AltAz
from astropy import units as u
from IPython import embed


FOCAL_LENGTH = u.Quantity(2.1500001, u.m)


def get_on_off_positions(path_gamma1deg, angles):
    with HDF5Reader(path_gamma1deg) as reader:
        df_mc = reader.read('mc').iloc[[0]]
        df_pointing = reader.read('pointing').iloc[[0]]

    telescope_pointing = get_telescope_pointing(df_pointing)
    engineering_frame = get_engineering_frame(
        telescope_pointing, focal_length=FOCAL_LENGTH
    )

    alt = df_mc['alt'].values[0]
    az = df_mc['az'].values[0]
    source_skycoord = SkyCoord(
        alt=alt, az=az, unit='rad', frame=telescope_pointing
    )
    rotated_skycoord = rotate_about_camera_centre(
        telescope_pointing, source_skycoord, angles
    )

    cam = rotated_skycoord.transform_to(engineering_frame)
    x = cam.x.value
    y = cam.y.value

    return x, y


def get_weights(df_mc, df_mcheader):
    df_mch = df_mcheader

    iobs = df_mc['iobs'].values
    energies = df_mc['energy'].values * u.TeV
    shower_primary_id = df_mc['shower_primary_id'].values
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

    print(f"Maximum t_norm: {t_norm_events.max()}")
    print(f"Total simulated: {n_simulated.sum()}")
    print(f"Total events: {energies.size}")

    return weights / t_norm_events


def get_dataframe(path, x_onoff, y_onoff):
    with HDF5Reader(path) as reader:
        df_hillas = reader.read('data')
        df_mc = reader.read('mc')
        df_mcheader = reader.read('mcheader')
        
        iobs = df_mc['iobs'].values
        mcheader = df_mcheader.copy()
        mcheader = mcheader.set_index('iobs').loc[iobs]

    x_cog = df_hillas['x'].values
    y_cog = df_hillas['y'].values
    psi = df_hillas['psi'].values
    for iangle in range(len(x_onoff)):
        alpha, alpha90 = calculate_alpha(
            x_onoff[iangle], y_onoff[iangle], x_cog, y_cog, psi
        )
        df_hillas[f'alpha_{iangle}'] = np.rad2deg(alpha90)
        df_hillas[f'xpos_{iangle}'] = x_onoff[iangle]
        df_hillas[f'ypos_{iangle}'] = y_onoff[iangle]

    energies = df_mc['energy'].values * u.TeV
    index = mcheader['spectral_index'].values
    e_min = mcheader['energy_range_min'].values * u.TeV
    e_max = mcheader['energy_range_max'].values * u.TeV
    area = (mcheader['max_scatter_range'].values * u.m) ** 2 * np.pi
    solid_angle = (mcheader['max_viewcone_radius'].values -
                   mcheader['min_viewcone_radius'].values) * u.deg

    df_hillas['weights'] = get_weights(df_mc, df_mcheader)

    df_hillas['energies'] = energies
    df_hillas['index'] = index
    df_hillas['e_min'] = e_min
    df_hillas['e_max'] = e_max
    df_hillas['area'] = area
    df_hillas['solid_angle'] = solid_angle
    df_hillas['diffuse'] = mcheader['diffuse'].values

    plate_scale = FOCAL_LENGTH.to_value(u.m) * np.pi/180
    df_hillas['r'] = df_hillas['r'].values / plate_scale
    df_hillas['width'] = df_hillas['width'].values / plate_scale
    df_hillas['length'] = df_hillas['length'].values / plate_scale

    return df_hillas


def process(path_gamma, path_proton, base_output, n_off):
    angles = np.linspace(0, 360, n_off+2)[:-1] * u.deg
    n_onoff = len(angles)
    print(angles)

    x_onoff, y_onoff = get_on_off_positions(path_gamma, angles)
    df_gamma = get_dataframe(path_gamma, x_onoff, y_onoff)
    df_proton = get_dataframe(path_proton, x_onoff, y_onoff)

    output_path = base_output + "_onoff.h5"
    with HDF5Writer(output_path) as writer:
        df_on = pd.concat([df_gamma, df_proton], ignore_index=True)
        df_on['alpha'] = df_on['alpha_0']
        df_off = df_proton.copy()
        df_off['alpha'] = df_off['alpha_0']
        for i in range(n_onoff):
            df_on.drop(f'alpha_{i}', axis=1, inplace=True)
            df_off.drop(f'alpha_{i}', axis=1, inplace=True)
        writer.write(on=df_on)
        writer.write(off=df_off)
        writer.add_metadata(alpha_li_ma=1)

    output_path = base_output + "_wobble.h5"
    with HDF5Writer(output_path) as writer:
        df = pd.concat([df_gamma, df_proton], ignore_index=True)
        df_on = df.copy()
        df_on['alpha'] = df_on['alpha_0']
        df_list = []
        for i in range(1, n_onoff):
            df_i = df.copy()
            df_i['alpha'] = df_i[f'alpha_{i}']
            df_list.append(df_i)
        df_off = pd.concat(df_list, ignore_index=True)
        for i in range(n_onoff):
            df_on.drop(f'alpha_{i}', axis=1, inplace=True)
            df_off.drop(f'alpha_{i}', axis=1, inplace=True)
        writer.write(on=df_on)
        writer.write(off=df_off)
        writer.add_metadata(alpha_li_ma=1/(n_onoff-1))


def process_gamma_only(path_gamma, base_output, n_off):
    angles = np.linspace(0, 360, n_off+2)[:-1] * u.deg
    n_onoff = len(angles)
    print(angles)

    x_onoff, y_onoff = get_on_off_positions(path_gamma, angles)
    df_gamma = get_dataframe(path_gamma, x_onoff, y_onoff)

    output_path = base_output + "_wobble.h5"
    with HDF5Writer(output_path) as writer:
        df = df_gamma
        df_on = df.copy()
        df_on['alpha'] = df_on['alpha_0']
        df_list = []
        for i in range(1, n_onoff):
            df_i = df.copy()
            df_i['alpha'] = df_i[f'alpha_{i}']
            df_list.append(df_i)
        df_off = pd.concat(df_list, ignore_index=True)
        for i in range(n_onoff):
            df_on.drop(f'alpha_{i}', axis=1, inplace=True)
            df_off.drop(f'alpha_{i}', axis=1, inplace=True)
        writer.write(on=df_on)
        writer.write(off=df_off)
        writer.add_metadata(alpha_li_ma=1/(n_onoff-1))


def main():
    path_gamma = get_astri_2019("d2019-05-15_simulations/gamma_1deg.h5")
    path_proton = get_astri_2019("d2019-05-15_simulations/proton.h5")
    base_output = get_data("d191018_alpha/extract_alpha_mc/d2019-05-15_simulations_gamma1deg")
    n_off = 1
    process(path_gamma, path_proton, base_output, n_off)

    path_gamma = get_astri_2019("d2019-05-15_simulations/gamma_1deg.h5")
    path_proton = get_astri_2019("d2019-05-15_simulations/proton.h5")
    base_output = get_data("d191018_alpha/extract_alpha_mc/d2019-05-15_simulations_gamma1deg_5off")
    n_off = 5
    process(path_gamma, path_proton, base_output, n_off)

    path_gamma = get_astri_2019("d2019-05-15_simulations/gamma_0deg.h5")
    path_proton = get_astri_2019("d2019-05-15_simulations/proton.h5")
    base_output = get_data("d191018_alpha/extract_alpha_mc/d2019-05-15_simulations_gamma0deg")
    n_off = 1
    process(path_gamma, path_proton, base_output, n_off)

    path_gamma = get_astri_2019("d2019-05-15_simulations/gamma_1deg.h5")
    base_output = get_data("d191018_alpha/extract_alpha_mc/d2019-05-15_simulations_gammaonly")
    n_off = 1
    process_gamma_only(path_gamma, base_output, n_off)

    path_gamma = get_astri_2019("d2019-10-03_simulations/gamma_3deg.h5")
    path_proton = get_astri_2019("d2019-10-03_simulations/proton.h5")
    base_output = get_data("d191018_alpha/extract_alpha_mc/d2019-10-03_simulations_gamma3deg")
    n_off = 1
    process(path_gamma, path_proton, base_output, n_off)

    path_gamma = get_astri_2019("d2019-10-03_simulations/gamma_3deg.h5")
    path_proton = get_astri_2019("d2019-10-03_simulations/proton.h5")
    base_output = get_data("d191018_alpha/extract_alpha_mc/d2019-10-03_simulations_gamma3deg_5off")
    n_off = 5
    process(path_gamma, path_proton, base_output, n_off)

    path_gamma = get_astri_2019("d2019-10-03_simulations/gamma_3deg.h5")
    base_output = get_data("d191018_alpha/extract_alpha_mc/d2019-10-03_simulations_gammaonly")
    n_off = 1
    process_gamma_only(path_gamma, base_output, n_off)


if __name__ == '__main__':
    main()
