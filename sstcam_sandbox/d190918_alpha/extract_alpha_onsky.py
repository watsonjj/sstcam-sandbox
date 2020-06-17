from CHECLabPy.core.io import HDF5Reader, HDF5Writer
from CHECOnsky.scripts_analysis.add_pointing_to_hillas import LOCATION, \
    EngineeringCameraFrame, calculate_alpha
from sstcam_sandbox import get_data
import numpy as np
import pandas as pd
from astropy.coordinates import SkyCoord, AltAz
from astropy import units as u
from IPython import embed


FOCAL_LENGTH = u.Quantity(2.1500001, u.m)


def get_telescope_pointing(df_pointing):
    obstime = df_pointing['t_cpu']
    alt = (df_pointing['altitude_raw'] +
           df_pointing['altitude_cor']).values
    az = (df_pointing['azimuth_raw'] +
          df_pointing['azimuth_cor']).values
    altaz_frame = AltAz(location=LOCATION, obstime=obstime)
    return SkyCoord(
        alt=alt,
        az=az,
        unit='rad',
        frame=altaz_frame,
    )


def get_engineering_frame(telescope_pointing):
    return EngineeringCameraFrame(
        n_mirrors=2,
        location=LOCATION,
        obstime=telescope_pointing.obstime,
        focal_length=FOCAL_LENGTH,
        telescope_pointing=telescope_pointing,
    )


def get_camera_coords(source_skycoord, telescope_pointing,
                      engineering_frame, angle):
    if angle.value == 0:
        off_skycoord = source_skycoord
    else:
        position_angle = telescope_pointing.position_angle(
            source_skycoord
        ).to(u.deg) - angle
        seperation = telescope_pointing.separation(source_skycoord)
        off_skycoord = telescope_pointing.directional_offset_by(
            position_angle=position_angle,
            separation=seperation
        )

    off_cam = off_skycoord.transform_to(engineering_frame)
    x_off = off_cam.x.value
    y_off = off_cam.y.value
    return x_off, y_off


# def get_dataframes(path, angles):
#     with HDF5Reader(path) as reader:
#         df_hillas = reader.read('data')
#
#     # Convert hillas to degrees
#     plate_scale = FOCAL_LENGTH.to_value(u.m) * np.pi/180
#     df_hillas['r'] = df_hillas['r'].values / plate_scale
#     df_hillas['width'] = df_hillas['width'].values / plate_scale
#     df_hillas['length'] = df_hillas['length'].values / plate_scale
#
#     telescope_pointing = get_telescope_pointing(df_hillas)
#     engineering_frame = get_engineering_frame(telescope_pointing)
#     source_ra = df_hillas['source_ra'].values
#     source_dec = df_hillas['source_dec'].values
#     source_skycoord = SkyCoord(source_ra, source_dec, unit='deg', frame='icrs')
#     x_cog = df_hillas['x'].values
#     y_cog = df_hillas['y'].values
#     psi = df_hillas['psi'].values
#
#     df_on = None
#     df_off_list = []
#     for iangle, angle in enumerate(angles):
#         print(iangle)
#         x_onoff, y_onoff = get_camera_coords(
#             source_skycoord, telescope_pointing, engineering_frame, angle
#         )
#
#         alpha, alpha90 = calculate_alpha(
#             x_onoff, y_onoff, x_cog, y_cog, psi
#         )
#
#         if angle.value == 0:
#             df_on = df_hillas.copy()
#             df_on['alpha'] = np.rad2deg(alpha90)
#             # assert np.allclose(df_source['source_x'].values, x_onoff)
#             # assert np.allclose(df_source['source_y'].values, y_onoff)
#         else:
#             df_off = df_hillas.copy()
#             df_off['alpha'] = np.rad2deg(alpha90)
#             df_off_list.append(df_off)
#
#     df_off = pd.concat(df_off_list, ignore_index=True, sort=False)
#
#     return df_on, df_off


def main():
    path = get_data("d190918_alpha/onsky_hillas.h5")
    n_off = 5
    angles = np.linspace(0, 360, n_off+2)[:-1] * u.deg

    with HDF5Reader(path) as reader:
        df_hillas = reader.read('data')

    # Convert hillas to degrees
    plate_scale = FOCAL_LENGTH.to_value(u.m) * np.pi/180
    df_hillas['r'] = df_hillas['r'].values / plate_scale
    df_hillas['width'] = df_hillas['width'].values / plate_scale
    df_hillas['length'] = df_hillas['length'].values / plate_scale

    df_list = []
    for angle in angles:
        df_copy = df_hillas.copy()
        df_copy['angle'] = angle
        df_list.append(df_copy)
    df = pd.concat(df_list, ignore_index=True)

    print("Defining SkyCoords")
    telescope_pointing = get_telescope_pointing(df)
    engineering_frame = get_engineering_frame(telescope_pointing)
    source_ra = df['source_ra'].values
    source_dec = df['source_dec'].values
    source_skycoord = SkyCoord(source_ra, source_dec, unit='deg', frame='icrs')
    x_cog = df['x'].values
    y_cog = df['y'].values
    psi = df['psi'].values
    embed()


    print("Transforming to engineering frame")
    position_angle = telescope_pointing.position_angle(
        source_skycoord
    ).to(u.deg) - df['angle'].values * u.deg
    seperation = telescope_pointing.separation(source_skycoord)
    off_skycoord = telescope_pointing.directional_offset_by(
        position_angle=position_angle,
        separation=seperation
    )
    off_cam = off_skycoord.transform_to(engineering_frame)
    x_angle = off_cam.x.value
    y_angle = off_cam.y.value
    df['seperation'] = seperation
    df['x_angle'] = x_angle
    df['y_angle'] = y_angle

    # print("Calculating Alpha")
    # alpha, alpha90 = calculate_alpha(
    #     x_angle, y_angle, x_cog, y_cog, psi
    # )
    # df['alpha'] = np.rad2deg(alpha90)
    #
    # print("Saving data")
    # df_on = df.loc[df['angle'] == 0]
    # df_off = df.loc[df['angle'] != 0]
    # n_on_regions = np.unique(df_on['angle'].values).size
    # n_off_regions = np.unique(df_off['angle'].values).size
    # print(n_on_regions, n_off_regions)
    # output = get_data("d190918_alpha/onsky_wobble.h5")
    # with HDF5Writer(output) as writer:
    #     writer.write(on=df_on)
    #     writer.write(off=df_off)
    #     writer.add_metadata(alpha_li_ma=n_on_regions/n_off_regions)
    #
    # df_on = df.loc[df['angle'] == 0]
    # df_off = df.loc[df['angle'] == 180]
    # n_on_regions = np.unique(df_on['angle'].values).size
    # n_off_regions = np.unique(df_off['angle'].values).size
    # print(n_on_regions, n_off_regions)
    # output = get_data("d190918_alpha/onsky_wobble_1off.h5")
    # with HDF5Writer(output) as writer:
    #     writer.write(on=df_on)
    #     writer.write(off=df_off)
    #     writer.add_metadata(alpha_li_ma=n_on_regions/n_off_regions)


if __name__ == '__main__':
    main()
