from CHECLabPy.core.io import SimtelReader, HDF5Writer
from CHECLabPySB import get_astri_2019
from CHECOnsky.calib.extractor import OnskyExtractor
import numpy as np
import pandas as pd
from tqdm import tqdm
from CHECLabPy.utils.waveform import BaselineSubtractor
from CHECLabPy.waveform_reducers.common import Common
from glob import glob


def main():
    # paths = glob(get_astri_2019("d2019-04-23_nudges/mc/*.simtel.gz"))
    # output = get_astri_2019("d2019-04-23_nudges/mc/charge.h5")
    paths = glob(get_astri_2019("d2019-04-23_nudges/mc_191011/*.simtel.gz"))
    output = get_astri_2019("d2019-04-23_nudges/mc_191011/charge.h5")

    with HDF5Writer(output) as writer:
        for path in paths:
            reader = SimtelReader(path)

            kw = dict(
                n_pixels=reader.n_pixels,
                n_samples=reader.n_samples,
                mapping=reader.mapping,
                reference_pulse_path=reader.reference_pulse_path,
            )
            baseline_subtractor = BaselineSubtractor(reader)
            extractor_onsky = OnskyExtractor(**kw)
            common = Common(**kw, _disable_by_default=True, waveform_max=True)

            pixel_array = np.arange(reader.n_pixels)

            desc = "Looping over file"
            for wfs in tqdm(reader, total=reader.n_events, desc=desc):
                iev = wfs.iev
                wfs = baseline_subtractor.subtract(wfs)

                params = dict(
                    iev=iev,
                    pixel=pixel_array,
                    onsky=extractor_onsky.process(wfs)['charge_onsky'],
                    waveform_max=common.process(wfs)['waveform_max'],
                    mc_true=wfs.mc_true,
                )

                df = pd.DataFrame(params)
                writer.append(df, key='data')


if __name__ == '__main__':
    main()
