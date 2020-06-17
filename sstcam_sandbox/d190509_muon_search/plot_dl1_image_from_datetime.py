from CHECOnsky.scripts_analysis.plot_dl1_image import ImagePlotter
from CHECLabPy.core.io import DL1Reader
from CHECLabPy.utils.mapping import get_ctapipe_camera_geometry
import argparse
from argparse import ArgumentDefaultsHelpFormatter as Formatter
from tqdm import tqdm
from os.path import join
from datetime import datetime
import numpy as np


def valid_datetime(s):
    try:
        return datetime.strptime(s, "%Y-%m-%d %H:%M")
    except ValueError:
        msg = "Not a valid datetime: '{0}'.".format(s)
        raise argparse.ArgumentTypeError(msg)


def main():
    description = 'Plot DL1 images'
    parser = argparse.ArgumentParser(description=description,
                                     formatter_class=Formatter)
    parser.add_argument('-f', '--file', dest='input_path', required=True,
                        help='path to the HDF5 dl1 file')
    parser.add_argument('-o', '--output', dest='output_dir',
                        help='directory to save the plots')
    parser.add_argument('-t', dest='datetime', required=True,
                        help='Datetime to plot from (UTC)',
                        type=valid_datetime)
    parser.add_argument('-m', dest='max_events',
                        help='Max events', type=int)
    args = parser.parse_args()

    input_path = args.input_path
    output = args.output_dir
    dt = args.datetime
    max_events = args.max_events

    if output is None:
        output = input_path.replace("_dl1.h5", "_dl1images_dt")

    with DL1Reader(input_path) as reader:
        n_events = reader.n_events
        n_pixels = reader.n_pixels
        mapping = reader.mapping
        if max_events and max_events < n_events:
            n_events = max_events

        print(f"Ordering events from datetime: {dt}")
        t_cpu = reader.select_column("t_cpu").values.reshape(
            (n_events, n_pixels)
        )[:, 0]
        t_delta = t_cpu - np.datetime64(dt)
        indicis = np.argsort(np.absolute(t_delta))
        if max_events:
            indicis = indicis[:max_events]

        p_image = ImagePlotter(mapping)
        desc = "Looping over events"
        for ientry, index in tqdm(enumerate(indicis), desc=desc):
            df = reader.select_event_index(index)
            iev = df['iev'].values[0]
            t_cpu = df['t_cpu'].values[0]

            image_c = df['photons'].values
            image_t = df['pulse_time'].values
            image_h = df['pulse_height'].values

            p_image.set_image(iev, image_c, image_t, image_h)
            p_image.fig.suptitle(f"Event: {iev}, Time: {t_cpu}")
            p_image.save(join(output, f"i{ientry}_e{iev}.png"))


if __name__ == '__main__':
    main()
