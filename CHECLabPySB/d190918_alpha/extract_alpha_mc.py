from CHECLabPy.core.io import HDF5Reader, HDF5Writer
from CHECOnsky.scripts_analysis.add_pointing_to_hillas import LOCATION, \
    FOCAL_LENGTH, EngineeringCameraFrame, calculate_alpha
from CHECLabPySB import get_data
from CHECLabPySB.d190918_alpha.spectra import norm_crab, norm_proton
import numpy as np
import pandas as pd
from astropy.coordinates import SkyCoord, AltAz
from astropy import units as u
from IPython import embed
from matplotlib import pyplot as plt


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
    print(f"MC RA/DEC Offset = {seperation} deg")
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
    df_hillas['weights'] = weights/t_norm
    df_hillas['diffuse'] = mcheader['diffuse']

    return df_hillas


def main():
    path_gamma1deg = "/Users/Jason/Downloads/tempdata/alpha/mc/gamma_1deg.h5"
    path_proton = "/Users/Jason/Downloads/tempdata/alpha/mc/proton.h5"
    # TODO: Electrons and gamma diffuse?
    output_path = get_data("d190918_alpha/alpha_mc.h5")

    angles = np.linspace(0, 360, 3)[:-1] * u.deg
    print(angles)
    x_onoff, y_onoff = get_on_off_positions(path_gamma1deg, angles)
    df_gamma1deg = get_dataframe(path_gamma1deg, x_onoff, y_onoff, norm_crab)
    df_proton = get_dataframe(path_proton, x_onoff, y_onoff, norm_proton)

    df = pd.concat([
        df_gamma1deg,
        df_proton,
    ], ignore_index=True)
    with HDF5Writer(output_path) as writer:
        writer.write(data=df)
        writer.add_metadata(n_onoff=len(angles))


if __name__ == '__main__':
    main()
