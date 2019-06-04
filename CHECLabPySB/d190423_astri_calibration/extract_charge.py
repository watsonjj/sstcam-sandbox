from CHECLabPy.core.io import ReaderR1, HDF5Writer
from CHECLabPySB import get_astri_2019
from CHECOnsky.calib.extractor import OnskyCalibExtractor, OnskyExtractor
import numpy as np
import pandas as pd
from tqdm import tqdm
from os.path import join, dirname
from CHECLabPy.calib import TimeCalibrator
from CHECLabPy.utils.waveform import BaselineSubtractor
from CHECLabPy.waveform_reducers.cross_correlation import CrossCorrelation
from CHECLabPy.waveform_reducers.common import Common
from CHECOnsky.calib import get_nudge_and_temperature_from_reader


def main():
    runlist_path = get_astri_2019("d2019-04-23_nudges/bright_50pe/runlist.txt")
    df_runlist = pd.read_csv(runlist_path, sep='\t')
    output = get_astri_2019("d2019-04-23_nudges/bright_50pe/charge.h5")

    with HDF5Writer(output) as writer:
        mapping = None
        for _, row in df_runlist.iterrows():
            run = row['run']
            nudge = int(row['nudge'])
            path = join(dirname(runlist_path), f"Run{run:05d}_r1.tio")
            reader = ReaderR1(path, max_events=500)
            mapping = reader.mapping

            kw = dict(
                n_pixels=reader.n_pixels,
                n_samples=reader.n_samples,
                mapping=reader.mapping,
                reference_pulse_path=reader.reference_pulse_path,
            )
            baseline_subtractor = BaselineSubtractor(reader)
            time_calibrator = TimeCalibrator()
            extractor_cc = CrossCorrelation(**kw)
            extractor_onsky_calib = OnskyCalibExtractor(**kw)
            extractor_onsky = OnskyExtractor(**kw)
            common = Common(**kw, _disable_by_default=True, waveform_max=True)

            pixel_array = np.arange(reader.n_pixels)

            monitor = get_nudge_and_temperature_from_reader(reader)
            nudge_from_dac, temperature = monitor
            assert nudge == nudge_from_dac

            desc = "Looping over file"
            for wfs in tqdm(reader, total=reader.n_events, desc=desc):
                iev = reader.index
                if reader.stale.any():
                    continue

                wfs = time_calibrator(wfs)
                wfs = baseline_subtractor.subtract(wfs)

                cc = extractor_cc.process(wfs)['charge_cc']
                onsky_calib = extractor_onsky_calib.process(wfs)[
                    'charge_onskycalib'
                ]
                onsky = extractor_onsky.process(wfs)['charge_onsky']
                waveform_max = common.process(wfs)['waveform_max']

                params = dict(
                    nudge=nudge,
                    nudge_from_dac=nudge_from_dac,
                    temperature=temperature,
                    iev=iev,
                    pixel=pixel_array,
                    cc=cc,
                    onsky_calib=onsky_calib,
                    onsky=onsky,
                    waveform_max=waveform_max,
                )

                df = pd.DataFrame(params)
                writer.append(df, key='data')

        writer.add_mapping(mapping)


if __name__ == '__main__':
    main()
