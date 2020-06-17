from glob import glob
from CHECLabPy.utils.files import sort_file_list
from CHECLabPy.core.io import HDF5Reader, DL1Reader, TIOReader
from sstcam_sandbox import get_data
from CHECOnsky.scripts_analysis.add_pointing_to_hillas import  \
    LOCATION, FOCAL_LENGTH
from astropy.coordinates import SkyCoord, AltAz
from ctapipe.coordinates import EngineeringCameraFrame
import pandas as pd
from IPython import embed


def add_camera_position(df_pointing, source_skycoord):
    obstime = df_pointing.index.values
    alt = df_pointing['altitude_raw'].values
    az = df_pointing['azimuth_raw'].values
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
        obstime=obstime,
        focal_length=FOCAL_LENGTH,
        telescope_pointing=telescope_pointing,
    )
    source_cam = source_skycoord.transform_to(engineering_frame)
    x_src = source_cam.x.value
    y_src = source_cam.y.value
    df_pointing['x_src'] = x_src
    df_pointing['y_src'] = y_src


def main():
    astri_db = "/Volumes/gct-jason/astri_onsky_archive/astri_db.h5"
    hillas_paths = sort_file_list(glob(
        "/Volumes/gct-jason/astri_onsky_archive/d2019-05-02_mrk421/*_hillas.h5"
    ))
    source_name = "mrk421"

    df_hillas_list = []
    readers = []
    mapping = None
    for ipath, hillas_path in enumerate(hillas_paths):
        dl1_path = hillas_path.replace("_hillas.h5", "_dl1.h5")
        r1_path = hillas_path.replace("_hillas.h5", "_r1.tio")
        hillas_reader = HDF5Reader(hillas_path)
        dl1_reader = DL1Reader(dl1_path)
        r1_reader = TIOReader(r1_path)

        if mapping is None:
            mapping = hillas_reader.get_mapping()

        df_data = hillas_reader.read("data")
        df_source = hillas_reader.read("source")
        df_merged = pd.merge(df_data, df_source)
        df_merged['ipath'] = ipath
        df_hillas_list.append(df_merged)
        readers.append((dl1_reader, r1_reader))
    df_hillas = pd.concat(df_hillas_list, ignore_index=True)
    df_hillas = df_hillas.set_index('t_cpu')

    # start_time = df_hillas.index[0]
    # end_time = df_hillas.index[-1]
    #
    # df_pointing = read_pointing_from_database(astri_db)
    # df_pointing = df_pointing.set_index('timestamp')[start_time:end_time]
    # source_table = Simbad.query_object(source_name)
    # source_skycoord = SkyCoord(
    #     ra=Angle(source_table["RA"], unit='hourangle'),
    #     dec=Angle(source_table["DEC"], unit='degree'),
    #     frame='icrs'
    # )
    # add_camera_position(df_pointing, source_skycoord)
    #
    # time_range = pd.Timedelta('1m')
    # max_alpha = 0.1
    # min_intensity = 500
    # d_list = []
    # for timestamp, row in df_pointing.iterrows():
    #     d = dict()
    #     df_within = df_hillas[timestamp-time_range:timestamp+time_range]
    #     df_within = df_within.loc[df_within['intensity'] > min_intensity]
    #     min_alpha_entry = df_within.sort_values("alpha90").iloc[0]
    #     if min_alpha_entry['alpha90'] < max_alpha:
    #         ipath = int(min_alpha_entry['ipath'])
    #         iev = int(min_alpha_entry['iev'])
    #         dl1_reader, r1_reader = readers[ipath]
    #         d['dl1'] = dl1_reader[iev]['photons'] * 0.25
    #         d['r1'] = r1_reader[iev]
    #         d['iev'] = iev
    #         d['iobs'] = min_alpha_entry['iobs']
    #         d['alpha'] = min_alpha_entry['alpha90']
    #         d['x_src'] = min_alpha_entry['source_x']
    #         d['y_src'] = min_alpha_entry['source_y']
    #         d['timestamp'] = min_alpha_entry.name
    #     else:
    #         d['x_src'] = row['x_src']
    #         d['y_src'] = row['y_src']
    #         d['timestamp'] = timestamp
    #     d_list.append(d)

    df_hillas_cut = df_hillas.loc[
        (df_hillas['image_max'] > 200) &
        (df_hillas['alpha90'] < 0.1) &
        (df_hillas['baseline_mean'] < 11.88) &
        (df_hillas['charge_median'] < 11) &
        (df_hillas['size_tm_20'] < 24.5) &
        (df_hillas['size_tm_40'] < 14.5)
    ]
    print(f"N_EVENTS: {df_hillas_cut.index.size}")
    if df_hillas_cut.index.size < 100:
        raise ValueError()

    d_list = []
    for timestamp, row in df_hillas_cut.iterrows():
        ipath = int(row['ipath'])
        iev = int(row['iev'])
        dl1_reader, r1_reader = readers[ipath]
        dl1_ev = dl1_reader[iev]
        d_list.append(dict(
            timestamp=timestamp,
            iev=iev,
            iobs=row['iobs'],
            dl1=dl1_ev['photons'] * 0.25,
            dl1_pulse_time=dl1_ev['pulse_time'],
            r1=r1_reader[iev],
            alpha=row['alpha90'],
            x_src=row['source_x'],
            y_src=row['source_y'],
            x_cog=row['x'],
            y_cog=row['y'],
            psi=row['psi'],
        ))

    df = pd.DataFrame(d_list)
    with pd.HDFStore(get_data("d190717_alpha/wobble.h5"), mode='w') as store:
        store['data'] = df
        store['mapping'] = mapping
        store.get_storer('mapping').attrs.metadata = mapping.metadata


if __name__ == '__main__':
    main()
