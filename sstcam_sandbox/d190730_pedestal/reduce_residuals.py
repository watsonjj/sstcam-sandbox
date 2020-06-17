from sstcam_sandbox.d190730_pedestal import all_files, Lab_bright
import numpy as np
from CHECLabPy.core.io import TIOReader
from CHECLabPy.calib.waveform import WaveformCalibrator
import dask
import dask.array as da


def get_event(reader, wf_calib, iev):
    wfs = reader[iev]
    fci = wfs.first_cell_id
    calibrated = wf_calib(wfs, fci)
    return calibrated


def get_da(reader, wf_calib):
    delayed_event = dask.delayed(get_event, pure=True)
    lazy_wfs = [
        delayed_event(reader, wf_calib, iev)
        for iev in range(reader.n_events)
    ]
    sample = lazy_wfs[0].compute()
    arrays = [
        da.from_delayed(lazy_image, dtype=sample.dtype, shape=sample.shape)
        for lazy_image in lazy_wfs
    ]
    stack = da.stack(arrays, axis=0)
    return stack


def process(input_path, pedestal_path, output_path):
    reader = TIOReader(input_path)
    wf_calib = WaveformCalibrator(
        pedestal_path, reader.n_pixels, reader.n_samples
    )

    wfs = get_da(reader, wf_calib)

    mean, std, mean_pix, std_pix, (hist, edges) = da.compute(
        wfs.mean(),
        wfs.std(),
        wfs.mean(axis=(0, 2)),
        wfs.std(axis=(0, 2)),
        da.histogram(wfs, bins=1000, range=(-10, 10))
    )

    np.savez(
        output_path,
        mean=mean,
        std=std,
        mean_pix=mean_pix,
        std_pix=std_pix,
        hist=hist,
        edges=edges
    )

    # between = (edges[1:] + edges[:-1]) / 2


def main():
    pedestal_path = Lab_bright().tcal
    for file in all_files:
        process(file.r0, pedestal_path, file.reduced_residuals)


if __name__ == '__main__':
    main()
