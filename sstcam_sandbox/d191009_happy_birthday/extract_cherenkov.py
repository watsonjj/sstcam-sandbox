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
from IPython import embed


def main():
    input_path = "event_list.txt"
    output_path = "cherenkov.npz"

    df = pd.read_csv(input_path, sep='\t')

    first_path = df.iloc[0]['path'].replace("_hillas.h5", "_r1.tio")
    first_reader = TIOReader(first_path)
    n_pixels = first_reader.n_pixels
    n_samples = first_reader.n_samples
    mapping = first_reader.mapping
    mapping.metadata['size'] *= 1.01  # TODO: WHY?!
    reference_pulse_path = first_reader.reference_pulse_path
    geom = get_ctapipe_camera_geometry(
        mapping
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

    n_events = df.index.size

    frames_array = []
    min_array = []
    max_array = []

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

        frames = shifted[:, st:et:4]
        min_ = np.full(frames.shape[-1], min_gf)
        max_ = np.full(frames.shape[-1], max_gf)

        frames_array.append(frames)
        min_array.append(min_)
        max_array.append(max_)

    np.savez(
        output_path,
        frames=np.column_stack(frames_array),
        min=np.concatenate(min_array),
        max=np.concatenate(max_array),
    )


if __name__ == '__main__':
    main()
