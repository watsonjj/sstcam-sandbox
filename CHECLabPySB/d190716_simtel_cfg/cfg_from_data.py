from CHECLabPySB import get_astri_2019, get_plot
from CHECLabPySB.d190716_simtel_cfg import generate_spectrum
from CHECLabPy.waveform_reducers.cross_correlation import CrossCorrelation
from CHECLabPy.calib import PixelMasks
import numpy as np
import pandas as pd
from target_calib import CameraConfiguration


def main():
    pm = PixelMasks()
    dead = np.where(np.logical_or(pm.dead, np.repeat(pm.bad_hv, 4)))[0]

    ref_path = CameraConfiguration("1.1.0").GetReferencePulsePath()
    cc = CrossCorrelation(1, 96, reference_pulse_path=ref_path)

    spe_path = get_astri_2019('d2019-04-23_nudges/spe_+0.h5')
    with pd.HDFStore(spe_path) as store:
        coeff = store['coeff_pixel']
        coeff = coeff.loc[~coeff['pixel'].isin(dead)]

    spe = cc.get_pulse_height(np.median(coeff['spe']))
    spe_sigma = cc.get_pulse_height(np.median(coeff['spe_sigma']))
    opct = np.median(coeff['opct'])

    output_dir = get_plot("d190716_simtel_cfg")
    generate_spectrum.call(output_dir, spe, spe_sigma, opct, 0, 0)


if __name__ == '__main__':
    main()
