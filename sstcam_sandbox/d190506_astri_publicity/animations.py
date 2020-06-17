from sstcam_sandbox.d190506_astri_publicity import d20190502_PG1553
from sstcam_sandbox import get_plot
from CHECLabPy.utils.mapping import get_ctapipe_camera_geometry
from CHECLabPy.core.io import TIOReader
from CHECLabPy.calib import TimeCalibrator
from CHECLabPy.waveform_reducers.cross_correlation \
    import CrossCorrelationNeighbour
from CHECOnsky.calib import AstriAmplitudeCalibrator, \
    get_nudge_and_temperature_from_reader
from CHECLabPy.plotting.camera import CameraImage
from CHECOnsky.calib import tailcut
from os.path import join, dirname
import numpy as np
from tqdm import tqdm
from matplotlib import animation


class CameraAnimation(CameraImage):
    def __init__(self, xpix, ypix, size, **kwargs):
        super().__init__(xpix, ypix, size, **kwargs)
        self.run = []
        self.iev = []
        self.time = []
        self.slice = []
        self.min = []
        self.max = []

    def add_image(self, run, iev, time, slice, min_, max_):
        self.run.append(run)
        self.iev.append(iev)
        self.time.append(time)
        self.slice.append(slice)
        self.min.append(min_)
        self.max.append(max_)

    def animate(self, interval, output_path):
        n_frames = len(self.slice)

        with tqdm(total=n_frames, desc="Creating animation") as pbar:
            def animate(i):
                pbar.update(1)
                run = self.run[i]
                iev = self.iev[i]
                time = self.time[i]
                slice = self.slice[i]
                min_ = self.min[i]
                max_ = self.max[i]
                # self.ax.set_title(f"RUN: {run}  IEV: {iev}  T: {time}")
                self.set_limits_minmax(min_, max_)
                self.image = slice
                return [self.pixels]

            anim = animation.FuncAnimation(
                self.fig, animate,
                frames=n_frames, interval=interval, blit=True
            )
            output_dir = dirname(output_path)
            self.create_directory(output_dir)
            anim.save(output_path, writer='imagemagick', dpi=150)
            print(f"Animation saved to: {output_path}")


def process(dataset):
    name = dataset.__class__.__name__
    directory = dataset.directory
    event_dict = dataset.events

    output_dir = get_plot(f"d190506_astri_publicity/{name}")
    goldfish_path = join(output_dir, 'goldfish.gif')
    image_path = join(output_dir, 'image.gif')

    first_run = list(event_dict.keys())[0]
    first_reader = TIOReader(join(directory, first_run+"_r1.tio"))
    mapping = first_reader.mapping

    p_image = CameraAnimation.from_mapping(mapping)
    p_image.add_colorbar("Amplitude (Photoelectons)")

    p_goldfish = CameraAnimation.from_mapping(mapping)
    p_goldfish.add_colorbar("Amplitude (mV)")

    for irun, run in enumerate(event_dict.keys()):
        print(f"Processing run: {run} ({irun+1}/{len(event_dict)})")
        path = join(directory, run+"_r1.tio")
        reader = TIOReader(path)
        n_events = reader.n_events
        n_pixels = reader.n_pixels
        n_samples = reader.n_samples
        reference_pulse_path = reader.reference_pulse_path
        geom = get_ctapipe_camera_geometry(
            mapping, plate_scale=37.56e-3
        )

        charge_extractor = CrossCorrelationNeighbour(
            n_pixels, n_samples,
            mapping=mapping,
            reference_pulse_path=reference_pulse_path,
        )
        time_calibrator = TimeCalibrator()
        nudge, temperature = get_nudge_and_temperature_from_reader(reader)
        amplitude_calibrator = AstriAmplitudeCalibrator(nudge, temperature)

        for event in tqdm(event_dict[run]):
            wfs = reader[event]

            shifted = time_calibrator(wfs)
            extracted = charge_extractor.process(shifted)
            charge = extracted['charge_cc_nn']
            time = extracted['t_cc_nn']
            photons = amplitude_calibrator(charge, np.arange(n_pixels))
            pe = photons * 0.25

            mask = tailcut(geom, photons, time)
            if not mask.any():
                msg = f"No pixels survived cleaning for: {run} {event}"
                # raise ValueError(msg)
                print(msg)
                three_largest = np.argsort(photons)[:-3]
                mask = np.zeros(n_pixels, dtype=np.bool)
                mask[three_largest] = True

            photons_nan = photons
            photons_nan[~mask] = np.nan

            min_pixel = np.nanargmin(photons_nan)
            max_pixel = np.nanargmax(photons_nan)

            min_image = 0
            max_image = 0.7 * pe.max()

            min_goldfish = shifted[max_pixel, :20].min()
            max_goldfish = shifted[max_pixel].max() * 0.8

            p_image.add_image(run, event, 0, pe, min_image, max_image)

            start_time = int(np.min(time[mask]) - 2)
            end_time = int(np.max(time[mask]) + 2)
            for t in range(start_time, end_time):
                if 0 <= t < n_samples:
                    p_goldfish.add_image(
                        run, event, t, shifted[:, t],
                        min_goldfish, max_goldfish
                    )

    p_image.animate(300, image_path)
    p_goldfish.animate(20, goldfish_path)


def main():
    datasets = [
        d20190502_PG1553()
    ]
    [process(d) for d in datasets]


if __name__ == '__main__':
    main()
