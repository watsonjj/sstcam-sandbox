from sstcam_sandbox.d190730_pedestal import Test, setup_cells
from CHECLabPy.core.io import HDF5Reader
from target_calib import PedestalArrayReader
import numpy as np
from astropy.io import fits
from IPython import embed


def main():
    file = Test()
    path_reduced = file.reduced_cell_info
    path_tcal = file.tcal

    with HDF5Reader(path_reduced) as reader:
        df = reader.read("data")
        poi = reader.get_metadata()['poi']

    df = setup_cells(df)
    gb = df.groupby(['fblock', 'fbpisam'])['adc']
    pedestal_reduced = gb.mean().unstack().values
    hits_reduced = gb.count().unstack().values
    std_reduced = gb.std().unstack().values

    tm = poi // 64
    tmpix = poi % 64

    ped_reader = PedestalArrayReader(path_tcal)
    pedestal_tcal = np.array(ped_reader.GetPedestal())[tm, tmpix]
    hits_tcal = np.array(ped_reader.GetHits())[tm, tmpix]
    std_tcal = np.array(ped_reader.GetStdDev())[tm, tmpix]
    header = fits.open(path_tcal)[0].header
    n_samplesbp = int(header['MAXSAMPLESBP']) + 1
    pedestal_tcal = pedestal_tcal[:, :n_samplesbp]
    hits_tcal = hits_tcal[:, :n_samplesbp]
    std_tcal = std_tcal[:, :n_samplesbp]

    print(f"Pedestal: {np.allclose(pedestal_reduced, pedestal_tcal)}")
    print(f"Hits: {np.allclose(hits_reduced, hits_tcal)}")
    print(f"StdDev: {np.allclose(std_reduced, std_tcal, rtol=1.e-4)}")

    # embed()


if __name__ == '__main__':
    main()
