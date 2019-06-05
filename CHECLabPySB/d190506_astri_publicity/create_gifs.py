from CHECLabPy.plotting.setup import Plotter
from CHECLabPy.plotting.camera import CameraImage
from CHECLabPy.utils.mapping import get_ctapipe_camera_geometry
from CHECLabPy.core.io import TIOReader
from CHECLabPy.calib import TimeCalibrator
from CHECOnsky.calib import OnskyAmplitudeCalibrator, \
    get_nudge_and_temperature_from_reader, OnskyExtractor
from CHECOnsky.calib import obtain_cleaning_mask
import argparse
from argparse import ArgumentDefaultsHelpFormatter as Formatter
from os.path import dirname, splitext, join
import numpy as np
import pandas as pd
from tqdm import tqdm
from matplotlib import animation
from matplotlib import pyplot as plt


class CameraAnimation(Plotter):
    def __init__(self, mapping, **kwargs):
        super().__init__(sidebyside=True, **kwargs)

        figsize = self.get_figsize()

        self.fig_image = plt.figure(figsize=figsize)
        self.ax_image = self.fig_image.add_subplot(1, 1, 1)
        self.ci_image = CameraImage.from_mapping(mapping, ax=self.ax_image)
        self.ci_image.add_colorbar("Pixel Amplitude (p.e.)", pad=-0.2)

        self.fig_gf = plt.figure(figsize=figsize)
        self.ax_gf = self.fig_gf.add_subplot(1, 1, 1)
        self.ci_gf = CameraImage.from_mapping(mapping, ax=self.ax_gf)
        self.ci_gf.add_colorbar("Pixel Amplitude (mV)", pad=-0.2)

        figsize_combined = figsize
        figsize_combined[0] *= 1.5
        self.fig_combined = plt.figure(figsize=figsize_combined)
        self.ax_cgf = self.fig_combined.add_subplot(1, 2, 1)
        self.ax_cimage = self.fig_combined.add_subplot(1, 2, 2)
        self.ci_cgf = CameraImage.from_mapping(mapping, ax=self.ax_cgf)
        # self.ci_cgf.add_colorbar("Pixel Amplitude (mV)", pad=0)
        self.ci_cimage = CameraImage.from_mapping(mapping, ax=self.ax_cimage)
        self.ci_cimage.add_colorbar("Pixel Amplitude (p.e.)", pad=0)
        self.fig_combined.subplots_adjust(
            left=0.01, right=0.95, top=0.95, bottom=0.05, wspace=0, hspace=0
        )

        self.meta = None
        self.image = None
        self.waveforms = None

    def set_meta(self, i, iobs, iev):
        self.meta = (i, iobs, iev)

    def set_image(self, image, min_, max_):
        self.image = (image, min_, max_)

    def set_waveforms(self, waveforms, min_, max_):
        self.waveforms = (waveforms, min_, max_)

    @property
    def n_timeslices(self):
        return self.waveforms[0].shape[1]

    def animate(self, output_dir, interval=20):
        dpi = 115

        dir_image = join(output_dir, "image")
        dir_goldfish = join(output_dir, "goldfish")
        dir_combined = join(output_dir, "combined")

        self.create_directory(dir_image)
        self.create_directory(dir_goldfish)
        self.create_directory(dir_combined)

        index, iobs, iev = self.meta
        filename = f"i{index}_r{iobs}_e{iev}"

        image, imin_, imax_ = self.image
        self.ci_image.set_limits_minmax(imin_, imax_)
        self.ci_image.image = image
        self.ci_image.save(join(dir_image, f"{filename}.png"), dpi=dpi)

        waveforms, fmin_, fmax_ = self.waveforms
        self.ci_gf.set_limits_minmax(fmin_, fmax_)
        self.ci_cgf.set_limits_minmax(fmin_, fmax_)
        self.ci_cimage.set_limits_minmax(imin_, imax_)
        self.ci_cimage.image = image
        with tqdm(total=self.n_timeslices*2, desc="Animating") as pbar:
            def animate_goldfish(i):
                pbar.update(1)
                frame = waveforms[:, i]
                self.ci_gf.image = frame

            def animate_combined(i):
                pbar.update(1)
                frame = waveforms[:, i]
                self.ci_cgf.image = frame

            anim_goldfish = animation.FuncAnimation(
                self.fig_gf, animate_goldfish, frames=self.n_timeslices,
                interval=interval
            )
            anim_goldfish.save(
                join(dir_goldfish, f"{filename}.gif"),
                writer='imagemagick', dpi=dpi
            )

            anim_combined = animation.FuncAnimation(
                self.fig_combined, animate_combined, frames=self.n_timeslices,
                interval=interval
            )
            anim_combined.save(
                join(dir_combined, f"{filename}.gif"),
                writer='imagemagick', dpi=dpi
            )


def main():
    description = 'Loop over R0 or R1 file and plot camera images'
    parser = argparse.ArgumentParser(description=description,
                                     formatter_class=Formatter)
    parser.add_argument('-f', '--file', dest='input_path', required=True,
                        help='path to a hillas list file created by '
                             'generate_list_from_hillas')
    parser.add_argument('-n', '--max_events', dest='max_events', type=int,
                        help='number of events to plot')
    args = parser.parse_args()

    input_path = args.input_path
    output_dir = splitext(input_path)[0]
    max_events = args.max_events

    df = pd.read_csv(input_path, sep='\t')

    first_path = df.iloc[0]['path'].replace("_hillas.h5", "_r1.tio")
    first_reader = TIOReader(first_path)
    n_pixels = first_reader.n_pixels
    n_samples = first_reader.n_samples
    mapping = first_reader.mapping
    mapping.metadata['size'] *= 1.01  # TODO: WHY?!
    reference_pulse_path = first_reader.reference_pulse_path
    geom = get_ctapipe_camera_geometry(
        mapping, plate_scale=37.56e-3
    )
    charge_extractor = OnskyExtractor(
        n_pixels, n_samples,
        mapping=mapping,
        reference_pulse_path=reference_pulse_path,
    )
    time_calibrator = TimeCalibrator()

    # Open all files
    hillas_paths = set()
    for _, row in df.iterrows():
        hillas_paths.add(row['path'])
    readers = dict()
    amplitude_calibrators = dict()
    for path in hillas_paths:
        r1_path = path.replace("_hillas.h5", "_r1.tio")
        reader = TIOReader(r1_path)
        nudge, temperature = get_nudge_and_temperature_from_reader(reader)
        amplitude_calibrator = OnskyAmplitudeCalibrator(nudge, temperature)
        readers[path] = reader
        amplitude_calibrators[path] = amplitude_calibrator

    p_animation = CameraAnimation(mapping)

    n_events = df.index.size
    if max_events is not None and n_events > max_events:
        n_events = max_events

    desc = "Looping over events"
    for i, row in tqdm(df.iterrows(), total=n_events, desc=desc):
        if i >= n_events:
            break

        hillas_path = row['path']
        iev = row['iev']
        iobs = row['iobs']

        reader = readers[hillas_path]
        amplitude_calibrator = amplitude_calibrators[hillas_path]

        waveforms = reader[iev]

        shifted = time_calibrator(waveforms)
        extracted = charge_extractor.process(shifted)
        charge = extracted['charge_onsky']
        time = extracted['t_onsky']
        photons = amplitude_calibrator(charge, np.arange(n_pixels))
        pe = photons * 0.25

        mask = obtain_cleaning_mask(geom, photons, time)
        if not mask.any():
            msg = f"No pixels survived cleaning for: RUN {iobs} IEV {iev}"
            raise ValueError(msg)

        photons_ma = np.ma.masked_array(photons, mask=~mask)

        min_pixel = photons_ma.argmin()
        max_pixel = photons_ma.argmax()

        min_image = -4
        max_image = 0.7 * pe.max()

        min_gf = shifted[max_pixel, :20].min()
        max_gf = shifted[max_pixel].max() * 0.8

        st = int(np.min(time[mask]) - 3)
        et = int(np.max(time[mask]) + 6)
        st = st if st > 0 else 0
        et = et if et < n_samples else n_samples

        p_animation.set_meta(i, iobs, iev)
        p_animation.set_image(pe, min_image, max_image)
        p_animation.set_waveforms(shifted[:, st:et:4], min_gf, max_gf)
        p_animation.animate(output_dir, interval=50)


if __name__ == '__main__':
    main()
