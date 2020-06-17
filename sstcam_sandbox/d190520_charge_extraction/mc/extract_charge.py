from CHECLabPy.core.io import SimtelReader, HDF5Writer
from CHECLabPy.waveform_reducers.cross_correlation import \
    CrossCorrelationLocal, CrossCorrelationNeighbour
from CHECLabPy.waveform_reducers.ctapipe_integrators import \
    CtapipeLocalPeakIntegrator, CtapipeNeighbourPeakIntegrator
from CHECLabPy.waveform_reducers.sliding_window import \
    SlidingWindowLocal, SlidingWindowNeighbour
from CHECLabPy.utils.waveform import BaselineSubtractor
from sstcam_sandbox import get_data
from glob import glob
import numpy as np
import pandas as pd
from tqdm import tqdm


def main():
    paths = glob("/Users/Jason/Data/d2019-04-23_nudges/mc/*.simtel.gz")
    output = get_data("d190520_charge_extraction/mc/charge.h5")

    # Use first run to initialise extractors
    reader = SimtelReader(paths[0])
    pixel_array = np.arange(reader.n_pixels)
    kw = dict(
        n_pixels=reader.n_pixels,
        n_samples=reader.n_samples,
        mapping=reader.mapping,
        reference_pulse_path=reader.reference_pulse_path,
    )
    extractors = dict(
        cc_local=(
            CrossCorrelationLocal(**kw), "charge_cc_local"
        ),
        cc_nn=(
            CrossCorrelationNeighbour(**kw), "charge_cc_nn"
        ),
        local_4_2=(
            CtapipeLocalPeakIntegrator(
                **kw, window_size=4, window_shift=2
            ), "charge_local"
        ),
        local_8_4=(
            CtapipeLocalPeakIntegrator(
                **kw, window_size=8, window_shift=4
            ), "charge_local"
        ),
        local_6_3=(
            CtapipeLocalPeakIntegrator(
                **kw, window_size=6, window_shift=3
            ), "charge_local"
        ),
        nn_4_2=(
            CtapipeNeighbourPeakIntegrator(
                **kw, window_size=4, window_shift=2
            ), "charge_nn"
        ),
        nn_8_4=(
            CtapipeNeighbourPeakIntegrator(
                **kw, window_size=8, window_shift=4
            ), "charge_nn"
        ),
        nn_6_3=(
            CtapipeNeighbourPeakIntegrator(
                **kw, window_size=6, window_shift=3
            ), "charge_nn"
        ),
        sliding_local_4=(
            SlidingWindowLocal(**kw, window_size=4), "charge_sliding_local"
        ),
        sliding_local_8=(
            SlidingWindowLocal(**kw, window_size=8), "charge_sliding_local"
        ),
        sliding_local_6=(
            SlidingWindowLocal(**kw, window_size=6), "charge_sliding_local"
        ),
        sliding_nn_4=(
            SlidingWindowNeighbour(**kw, window_size=4), "charge_sliding_nn"
        ),
        sliding_nn_8=(
            SlidingWindowNeighbour(**kw, window_size=8), "charge_sliding_nn"
        ),
        sliding_nn_6=(
            SlidingWindowNeighbour(**kw, window_size=6), "charge_sliding_nn"
        ),
    )

    with HDF5Writer(output) as writer:
        for ipath, path in enumerate(paths):
            print(f"Processing file {ipath+1}/{len(paths)}")
            reader = SimtelReader(path)
            baseline_subtractor = BaselineSubtractor(reader)
            n_events = reader.n_events
            for waveforms in tqdm(reader, total=n_events):
                params = dict()
                # TODO: Baseline subtraction
                waveforms = baseline_subtractor.subtract(waveforms)

                for key, (extractor, column) in extractors.items():
                    params[key] = extractor.process(waveforms)[column]

                params['iobs'] = ipath
                params['iev'] = waveforms.iev
                params['pixel'] = pixel_array
                params['true'] = waveforms.mc_true

                writer.append(pd.DataFrame(params), key='data')


if __name__ == '__main__':
    main()
