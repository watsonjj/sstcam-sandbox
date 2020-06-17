from CHECLabPy.plotting.setup import Plotter
from CHECLabPy.plotting.camera import CameraImage
from CHECLabPy.core.io import DL1Reader
from CHECLabPy.utils.mapping import get_ctapipe_camera_geometry
from sstcam_sandbox import get_plot
from CHECOnsky.calib import obtain_cleaning_mask, extract_image_parameters
from ctapipe.image.hillas import HillasParameterizationError, \
    hillas_parameters, camera_to_shower_coordinates
from ctapipe.image.timing_parameters import timing_parameters
import numpy as np
from numpy.polynomial.polynomial import polyfit, polyval
import pandas as pd
from tqdm import tqdm
from glob import glob
from IPython import embed


class RelationPlotter(Plotter):
    def plot(self, longi, peakpos, intensity):
        self.ax.plot(longi, peakpos, '.')

        c = polyfit(longi, peakpos, 1, w=np.sqrt(intensity))
        x = np.linspace(longi.min(), longi.max(), 10)
        y = polyval(x, c)
        self.ax.plot(x, y)

        self.ax.set_xlabel("Longtudinal distance from CoG along axis (degrees)")
        self.ax.set_ylabel("Pulse time (ns)")


def main():
    paths = [
        "/Volumes/gct-jason/astri_onsky_archive/d2019-05-15_simulations/proton/run1_dl1.h5",
    ]

    df_list = []

    for ipath, path in enumerate(paths):
        with DL1Reader(path) as reader:
            n_events = reader.get_metadata()['n_events']
            mapping = reader.get_mapping()
            geom = get_ctapipe_camera_geometry(
                mapping, plate_scale=37.56e-3
            )

            desc = "Looping over events"
            it = reader.iterate_over_events()
            for df in tqdm(it, total=n_events, desc=desc):
                iev = df['iev'].values[0]

                image = df['photons'].values
                time = df['pulse_time'].values

                mask = obtain_cleaning_mask(geom, image, time)
                if not mask.any():
                    continue

                image_m = image[mask]
                time_m = time[mask]
                geom_m = geom[mask]

                try:
                    hillas = hillas_parameters(geom_m, image_m)
                except HillasParameterizationError:
                    continue

                # timing_parameters(geom_m, image_m, time_m, hillas)

                gt0 = image_m > 0
                pix_x = geom_m.pix_x[gt0]
                pix_y = geom_m.pix_y[gt0]
                peakpos = time_m[gt0]
                intensity = image_m[gt0]

                longi, trans = camera_to_shower_coordinates(
                    pix_x,
                    pix_y,
                    hillas.x,
                    hillas.y,
                    hillas.psi
                )
                longi = longi.value
                trans = trans.value

                # df_list.append(pd.DataFrame(dict(
                #     ipath=ipath,
                #     iev=iev,
                #     longi=longi,
                #     peakpos=peakpos,
                # )))

                p_relation = RelationPlotter()
                p_relation.plot(longi, peakpos, intensity)
                p_relation.save(get_plot(f"d190524_time_gradient/relation/i{ipath}_e{iev}.pdf"))

    # embed()


if __name__ == '__main__':
    main()
