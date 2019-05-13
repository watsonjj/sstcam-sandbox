from CHECLabPy.plotting.camera import CameraImage
from CHECLabPy.utils.mapping import get_ctapipe_camera_geometry
from CHECLabPy.core.io import TIOReader
from CHECLabPy.calib import TimeCalibrator
from CHECLabPy.waveform_reducers.cross_correlation \
    import CrossCorrelationNeighbour
from CHECOnsky.calib import AstriAmplitudeCalibrator, \
    get_nudge_and_temperature_from_reader
from CHECOnsky.calib import tailcut
import argparse
from argparse import ArgumentDefaultsHelpFormatter as Formatter
from os.path import dirname, splitext, join
import numpy as np
import pandas as pd
from tqdm import tqdm
from matplotlib import animation


class CameraAnimation(CameraImage):
    def __init__(self, xpix, ypix, size, **kwargs):
        super().__init__(xpix, ypix, size, **kwargs)
        self.frames = []
        self.mins = []
        self.maxs = []

    def add_frame(self, frame, min_, max_):
        self.frames.append(frame)
        self.mins.append(min_)
        self.maxs.append(max_)

    def animate(self, interval, output_path):
        n_frames = len(self.frames)

        with tqdm(total=n_frames, desc="Creating animation") as pbar:
            def animate(i):
                pbar.update(1)
                frame = self.frames[i]
                min_ = self.mins[i]
                max_ = self.maxs[i]
                self.set_limits_minmax(min_, max_)
                self.image = frame
                return [self.pixels]

            anim = animation.FuncAnimation(
                self.fig, animate,
                frames=n_frames, interval=interval, blit=True
            )
            output_dir = dirname(output_path)
            self.create_directory(output_dir)
            anim.save(output_path, writer='imagemagick', dpi=150)
            # print(f"Animation saved to: {output_path}")


def main():
    description = 'Loop over R0 or R1 file and plot camera images'
    parser = argparse.ArgumentParser(description=description,
                                     formatter_class=Formatter)
    parser.add_argument('-f', '--file', dest='input_path', required=True,
                        help='path to a hillas list file created by '
                             'generate_list_from_hillas')
    args = parser.parse_args()

    input_path = args.input_path
    output_dir = splitext(input_path)[0]

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
    charge_extractor = CrossCorrelationNeighbour(
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
        amplitude_calibrator = AstriAmplitudeCalibrator(nudge, temperature)
        readers[path] = reader
        amplitude_calibrators[path] = amplitude_calibrator

    desc = "Looping over events"
    for i, row in tqdm(df.iterrows(), total=df.index.size, desc=desc):
        hillas_path = row['path']
        iev = row['iev']
        iobs = row['iobs']

        reader = readers[hillas_path]
        amplitude_calibrator = amplitude_calibrators[hillas_path]

        waveforms = reader[iev]

        shifted = time_calibrator(waveforms)
        extracted = charge_extractor.process(shifted)
        charge = extracted['charge_cc_nn']
        time = extracted['t_cc_nn']
        photons = amplitude_calibrator(charge, np.arange(n_pixels))
        pe = photons * 0.25

        mask = tailcut(geom, photons, time)
        if not mask.any():
            msg = f"No pixels survived cleaning for: RUN {iobs} IEV {iev}"
            raise ValueError(msg)

        photons_ma = np.ma.masked_array(photons, mask=~mask)

        min_pixel = photons_ma.argmin()
        max_pixel = photons_ma.argmax()

        min_image = -5
        max_image = 0.7 * pe.max()

        min_goldfish = shifted[max_pixel, :20].min()
        max_goldfish = shifted[max_pixel].max() * 0.8

        p_image_path = join(output_dir, f"image/i{i}_r{iobs}_e{iev}.gif")
        p_image = CameraAnimation.from_mapping(mapping)
        p_image.add_colorbar("Amplitude (Photoelectons)")
        p_image.add_frame(pe, min_image, max_image)
        p_image.animate(300, p_image_path)
        p_image.close()

        p_goldfish_path = join(output_dir, f"goldfish/i{i}_r{iobs}_e{iev}.gif")
        p_goldfish = CameraAnimation.from_mapping(mapping)
        p_goldfish.add_colorbar("Amplitude (mV)")
        start_time = int(np.min(time[mask]) - 3)
        end_time = int(np.max(time[mask]) + 3)
        for t in range(start_time, end_time):
            if 0 <= t < n_samples:
                p_goldfish.add_frame(shifted[:, t], min_goldfish, max_goldfish)
        p_goldfish.animate(20, p_goldfish_path)
        p_goldfish.close()


if __name__ == '__main__':
    main()
