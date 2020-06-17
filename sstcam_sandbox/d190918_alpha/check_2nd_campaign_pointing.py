from sstcam_sandbox import get_astri_2019
from CHECLabPy.plotting.setup import Plotter
from CHECOnsky.scripts_analysis.add_pointing_to_hillas import LOCATION
from CHECOnsky.utils.astri_database import ASTRISQLQuerier
from sstcam_sandbox import get_plot
from CHECLabPy.core.io import HDF5Reader
import numpy as np
import pandas as pd
from astropy.coordinates import SkyCoord, AltAz, EarthLocation
from IPython import embed


def main():
    path = get_astri_2019("astri_db.h5")
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

    df = df.query(
        " (timestamp > '2019-06-12 18:00')"
        "&(timestamp < '2019-06-13 05:00')"
    )

    embed()

    altaz_frame = AltAz(location=LOCATION, obstime=df['timestamp'].values)
    telescope_pointing = SkyCoord(
        alt=df['alt'].values,
        az=df['az'].values,
        unit='deg',
        frame=altaz_frame,
    )
    telescope_pointing_icrs = telescope_pointing.icrs
    df['ra_calc'] = telescope_pointing_icrs.ra.deg
    df['dec_calc'] = telescope_pointing_icrs.dec.deg

    d_ra = np.arctan2(
        np.sin(df['ra'] - df['ra_calc']),
        np.cos(df['ra'] - df['ra_calc'])
    )
    d_dec = np.arctan2(
        np.sin(df['dec'] - df['dec_calc']),
        np.cos(df['dec'] - df['dec_calc'])
    )

    p = Plotter()
    p.ax.plot(df['timestamp'], d_ra)
    p.ax.set_xlabel("Timestamp")
    p.ax.set_ylabel("RA_database - RA_calculated (deg)")
    p.fig.autofmt_xdate()
    p.save(get_plot("d190918_alpha/pointing/ra.pdf"))

    p = Plotter()
    p.ax.plot(df['timestamp'], d_dec)
    p.ax.set_xlabel("Timestamp")
    p.ax.set_ylabel("DEC_database - DEC_calculated (deg)")
    p.fig.autofmt_xdate()
    p.save(get_plot("d190918_alpha/pointing/dec.pdf"))


if __name__ == '__main__':
    main()
