from CHECLabPy.core.io import HDF5Reader, HDF5Writer
from CHECOnsky.scripts_analysis.add_pointing_to_hillas import LOCATION, \
    EngineeringCameraFrame, calculate_alpha
from CHECLabPySB import get_data, get_astri_2019
from CHECLabPySB.d190918_alpha.spectra import norm_crab, norm_proton
import numpy as np
import pandas as pd
from astropy.coordinates import SkyCoord, AltAz
from astropy import units as u
from IPython import embed
from matplotlib import pyplot as plt


FOCAL_LENGTH = u.Quantity(2.1500001, u.m)


def get_on_off_positions(path_gamma1deg, angles):
    with HDF5Reader(path_gamma1deg) as reader:
        df_source = reader.read('source')
        df_pointing = reader.read('pointing')

    obstime = df_pointing['t_cpu'].values[0]
    alt = (df_pointing['altitude_raw'] +
           df_pointing['altitude_cor']).values[0]
    az = (df_pointing['azimuth_raw'] +
          df_pointing['azimuth_cor']).values[0]
    altaz_frame = AltAz(location=LOCATION, obstime=obstime)
    telescope_pointing = SkyCoord(
        alt=alt,
        az=az,
        unit='rad',
        frame=altaz_frame,
    )
    engineering_frame = EngineeringCameraFrame(
        n_mirrors=2,
        location=LOCATION,
        obstime=telescope_pointing.obstime,
        focal_length=FOCAL_LENGTH,
        telescope_pointing=telescope_pointing,
    )

    source_ra = df_source['source_ra'].values[0]
    source_dec = df_source['source_dec'].values[0]

    source_skycoord = SkyCoord(source_ra, source_dec, unit='deg', frame='icrs')
    position_angle = telescope_pointing.position_angle(
        source_skycoord
    ).to(u.deg) - angles
    seperation = telescope_pointing.separation(source_skycoord)
    print(f"MC RA/DEC Offset = {seperation}")
    skycoords = telescope_pointing.directional_offset_by(
        position_angle=position_angle,
        separation=seperation
    )

    cam = skycoords.transform_to(engineering_frame)
    x = cam.x.value
    y = cam.y.value

    return x, y


def get_dataframe(path, x_onoff, y_onoff, norm_func):
    with HDF5Reader(path) as reader:
        df_hillas = reader.read('data')
        df_mc = reader.read('mc')
        mcheader = reader.read('mcheader').iloc[0]

    x_cog = df_hillas['x'].values
    y_cog = df_hillas['y'].values
    psi = df_hillas['psi'].values
    for iangle in range(len(x_onoff)):
        alpha, alpha90 = calculate_alpha(
            x_onoff[iangle], y_onoff[iangle], x_cog, y_cog, psi
        )
        df_hillas[f'alpha{iangle}'] = np.rad2deg(alpha90)

    energies = df_mc['energy'].values * u.TeV
    index = mcheader['spectral_index']
    e_min = mcheader['energy_range_min'] * u.TeV
    e_max = mcheader['energy_range_max'] * u.TeV
    area = (mcheader['max_scatter_range'] * u.m) ** 2 * np.pi
    solid_angle = (mcheader['max_viewcone_radius'] -
                   mcheader['min_viewcone_radius']) * u.deg
    weights, t_norm = norm_func(
        e_min, e_max, area, solid_angle, index, energies
    )
    df_hillas['energies'] = energies
    df_hillas['index'] = index
    df_hillas['e_min'] = e_min
    df_hillas['e_max'] = e_max
    df_hillas['area'] = area
    df_hillas['solid_angle'] = solid_angle
    df_hillas['weights'] = weights/t_norm
    df_hillas['diffuse'] = mcheader['diffuse']

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
    df_gamma = get_dataframe(path_gamma, x_onoff, y_onoff, norm_crab)
    df_proton = get_dataframe(path_proton, x_onoff, y_onoff, norm_proton)

    output_path = base_output + "_onoff.h5"
    with HDF5Writer(output_path) as writer:
        df_on = pd.concat([df_gamma, df_proton])
        df_on['alpha'] = df_on['alpha0']
        df_off = df_proton.copy()
        df_off['alpha'] = df_off['alpha0']
        for i in range(n_onoff):
            df_on.drop(f'alpha{i}', axis=1, inplace=True)
            df_off.drop(f'alpha{i}', axis=1, inplace=True)
        writer.write(on=df_on)
        writer.write(off=df_off)
        writer.add_metadata(alpha_li_ma=1)

    output_path = base_output + "_wobble.h5"
    with HDF5Writer(output_path) as writer:
        df = pd.concat([df_gamma, df_proton])
        df_on = df.copy()
        df_on['alpha'] = df_on['alpha0']
        df_list = []
        for i in range(1, n_onoff):
            df_i = df.copy()
            df_i['alpha'] = df_i[f'alpha{i}']
            df_list.append(df_i)
        df_off = pd.concat(df_list, ignore_index=True)
        for i in range(n_onoff):
            df_on.drop(f'alpha{i}', axis=1, inplace=True)
            df_off.drop(f'alpha{i}', axis=1, inplace=True)
        writer.write(on=df_on)
        writer.write(off=df_off)
        writer.add_metadata(alpha_li_ma=1/(n_onoff-1))


def process_gamma_only(path_gamma, base_output, n_off):
    angles = np.linspace(0, 360, n_off+2)[:-1] * u.deg
    n_onoff = len(angles)
    print(angles)

    x_onoff, y_onoff = get_on_off_positions(path_gamma, angles)
    df_gamma = get_dataframe(path_gamma, x_onoff, y_onoff, norm_crab)

    output_path = base_output + "_wobble.h5"
    with HDF5Writer(output_path) as writer:
        df = df_gamma
        df_on = df.copy()
        df_on['alpha'] = df_on['alpha0']
        df_list = []
        for i in range(1, n_onoff):
            df_i = df.copy()
            df_i['alpha'] = df_i[f'alpha{i}']
            df_list.append(df_i)
        df_off = pd.concat(df_list, ignore_index=True)
        for i in range(n_onoff):
            df_on.drop(f'alpha{i}', axis=1, inplace=True)
            df_off.drop(f'alpha{i}', axis=1, inplace=True)
        writer.write(on=df_on)
        writer.write(off=df_off)
        writer.add_metadata(alpha_li_ma=1/(n_onoff-1))


def main():
    path_gamma = get_astri_2019("d2019-05-15_simulations/gamma_1deg.h5")
    path_proton = get_astri_2019("d2019-05-15_simulations/proton.h5")
    base_output = get_data("d190918_alpha/extract_alpha_mc/d2019-05-15_simulations_gamma1deg")
    n_off = 1
    process(path_gamma, path_proton, base_output, n_off)

    path_gamma = get_astri_2019("d2019-05-15_simulations/gamma_1deg.h5")
    path_proton = get_astri_2019("d2019-05-15_simulations/proton.h5")
    base_output = get_data("d190918_alpha/extract_alpha_mc/d2019-05-15_simulations_gamma1deg_5off")
    n_off = 5
    process(path_gamma, path_proton, base_output, n_off)

    path_gamma = get_astri_2019("d2019-05-15_simulations/gamma_0deg.h5")
    path_proton = get_astri_2019("d2019-05-15_simulations/proton.h5")
    base_output = get_data("d190918_alpha/extract_alpha_mc/d2019-05-15_simulations_gamma0deg")
    n_off = 1
    process(path_gamma, path_proton, base_output, n_off)

    path_gamma = get_astri_2019("d2019-05-15_simulations/gamma_1deg.h5")
    path_proton = path_gamma
    base_output = get_data("d190918_alpha/extract_alpha_mc/d2019-05-15_simulations_gammaonly")
    n_off = 1
    process_gamma_only(path_gamma, base_output, n_off)


if __name__ == '__main__':
    main()
