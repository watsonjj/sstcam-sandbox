from CHECLabPy.plotting.setup import Plotter
from CHECLabPySB.d190527_astri_sql.sqlquerier import SQLQuerier
from CHECLabPySB import get_plot
from CHECLabPy.core.io import HDF5Reader
import pandas as pd
from astropy.coordinates import SkyCoord, AltAz, EarthLocation


def main():
    # sql = SQLQuerier()
    # start = pd.Timestamp("2019-04-29 00:00")
    # end = pd.Timestamp("2019-05-13 00:00")
    # ra = sql.get_table_between_datetimes("TCU_ACTUAL_RA", start, end)
    # dec = sql.get_table_between_datetimes("TCU_ACTUAL_DEC", start, end)
    # alt = sql.get_table_between_datetimes("TCU_ELACTPOS", start, end)
    # az = sql.get_table_between_datetimes("TCU_AZACTPOS", start, end)

    # path = get_astri_2019("astri_database_d190429-d190513.h5")
    path = "/Volumes/ICYBOX/astri_onsky_archive/astri_database_d190429-d190513.h5"
    with HDF5Reader(path) as reader:
        ra = reader.read("TCU_ACTUAL_RA")
        dec = reader.read("TCU_ACTUAL_DEC")
        alt = reader.read("TCU_ELACTPOS")
        az = reader.read("TCU_AZACTPOS")

    df = pd.merge(
        pd.merge(ra, dec, on='timestamp').rename(columns=dict(
            value_x="ra",
            value_y="dec"
        )),
        pd.merge(alt, az, on='timestamp').rename(columns=dict(
            value_x="alt",
            value_y="az"
        )),
        on='timestamp'
    )

    location = EarthLocation.from_geodetic(
        lon=14.974609, lat=37.693267, height=1750
    )
    altaz_frame = AltAz(location=location, obstime=df['timestamp'])
    telescope_pointing = SkyCoord(
        alt=df['alt'].values,
        az=df['az'].values,
        unit='deg',
        frame=altaz_frame,
    )
    telescope_pointing_icrs = telescope_pointing.icrs
    df['ra_calc'] = telescope_pointing_icrs.ra.deg
    df['dec_calc'] = telescope_pointing_icrs.dec.deg

    p = Plotter()
    p.ax.plot(df['timestamp'], df['ra'] - df['ra_calc'])
    p.ax.set_xlabel("Timestamp")
    p.ax.set_ylabel("RA_database - RA_calculated (deg)")
    p.fig.autofmt_xdate()
    p.save(get_plot("d190527_astri_sql/ra.pdf"))

    p = Plotter()
    p.ax.plot(df['timestamp'], df['dec'] - df['dec_calc'])
    p.ax.set_xlabel("Timestamp")
    p.ax.set_ylabel("DEC_database - DEC_calculated (deg)")
    p.fig.autofmt_xdate()
    p.save(get_plot("d190527_astri_sql/dec.pdf"))


if __name__ == '__main__':
    main()
