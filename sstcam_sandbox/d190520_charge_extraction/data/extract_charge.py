from CHECLabPy.core.io import ReaderR1, HDF5Writer
from sstcam_sandbox import get_data, get_astri_2019
import pandas as pd
from tqdm import tqdm
from CHECLabPy.calib import TimeCalibrator
from CHECLabPy.utils.waveform import BaselineSubtractor
from CHECLabPy.waveform_reducers.cross_correlation import \
    CrossCorrelationNeighbour
from CHECLabPy.waveform_reducers.ctapipe_integrators import \
    CtapipeNeighbourPeakIntegrator
from CHECLabPy.waveform_reducers.sliding_window import SlidingWindowNeighbour
from IPython import embed


def main():
    r1_paths = dict(
        off=get_astri_2019("d2019-05-08_ledflashers_dynrange/Run13268_r1.tio"),
        on_50=get_astri_2019("d2019-05-08_ledflashers_dynrange/Run13272_r1.tio"),
        on_3=get_astri_2019("d2019-05-08_ledflashers_dynrange/Run13267_r1.tio")
    )
    output = get_data("d190520_charge_extraction/data/charge.h5")
    poi = 2004

    reader = ReaderR1(list(r1_paths.values())[0])
    kw = dict(
        n_pixels=reader.n_pixels,
        n_samples=reader.n_samples,
        mapping=reader.mapping,
        reference_pulse_path=reader.reference_pulse_path,
    )
    extractors = dict(
        cc_nn=(CrossCorrelationNeighbour(**kw), 'charge_cc_nn'),
    )
    for width in range(1, 15):
        extractors[f'sliding_{width}'] = (
            SlidingWindowNeighbour(**kw, window_size=width),
            "charge_sliding_nn"
        )

        for shift in range(-3, 8):
            extractors[f'peak_{width}_{shift}'] = (
                CtapipeNeighbourPeakIntegrator(
                    **kw, window_size=width, window_shift=shift
                ), "charge_nn"
            )

    with HDF5Writer(output) as writer:
        for key, path in r1_paths.items():
            reader = ReaderR1(path, max_events=500)
            baseline_subtractor = BaselineSubtractor(reader)
            time_calibrator = TimeCalibrator()

            desc = "Looping over file"
            for wfs in tqdm(reader, total=reader.n_events, desc=desc):
                iev = wfs.iev
                if reader.stale.any():
                    continue

                wfs = time_calibrator(wfs)
                wfs = baseline_subtractor.subtract(wfs)

                global_params = dict(
                    key=key,
                    iev=iev,
                    pixel=poi,
                )

                for name, (extractor, column) in extractors.items():
                    params = global_params.copy()
                    params['extractor'] = name
                    params['charge'] = extractor.process(wfs)[column][poi]
                    df = pd.DataFrame(params, index=[0])
                    writer.append(df, key='data')


if __name__ == '__main__':
    main()
