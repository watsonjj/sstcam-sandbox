from CHECLabPy.core.io import TIOReader
from TargetCalibSB.pedestal import PedestalTargetCalib
import fitsio
from tqdm import tqdm
from matplotlib import pyplot as plt
import numpy as np


def main():
    r0_path = "/Users/Jason/Downloads/tempdata/Pedestal_23deg_r0.tio"
    r1_int_path = "/Users/Jason/Downloads/tempdata/Pedestal_23deg_r1_int.tio"
    r1_rnd_path = "/Users/Jason/Downloads/tempdata/Pedestal_23deg_r1_rnd.tio"
    tcal_path = "/Users/Jason/Downloads/tempdata/Pedestal_23deg_ped.tcal"

    reader_r0 = TIOReader(r0_path, max_events=10000)
    reader_r1_int = TIOReader(r1_int_path, max_events=10000)
    reader_r1_rnd = TIOReader(r1_rnd_path, max_events=10000)

    # Generate Pedestal
    pedestal_tc = PedestalTargetCalib(
        reader_r0.n_pixels, reader_r0.n_samples, reader_r0.n_cells
    )
    pedestal_tc.load_tcal(tcal_path)

    l_int = []
    l_rnd = []

    # Subtract Pedestals
    desc = "Subtracting pedestal"
    z = zip(reader_r0, reader_r1_int, reader_r1_rnd)
    it = tqdm(z, total=reader_r0.n_events, desc=desc)
    for wfs_r0, wfs_r1_int, wfs_r1_rnd in it:
        if wfs_r0.missing_packets:
            continue

        wfs_r1_flt = pedestal_tc.subtract_pedestal(wfs_r0, wfs_r0.first_cell_id)

        # offset = 700
        # scale = 13.6
        # wfs_r1_flt = (wfs_r1_flt + offset) * scale
        # wfs_r1_int = (wfs_r1_int + offset) * scale
        # wfs_r1_rnd = (wfs_r1_rnd + offset) * scale

        l_int.append(wfs_r1_flt - wfs_r1_int)
        l_rnd.append(wfs_r1_flt - wfs_r1_rnd)

    l_int = np.array(l_int).ravel()
    l_rnd = np.array(l_rnd).ravel()

    plt.hist(l_int, bins=20, histtype='step', label='int')
    plt.hist(l_rnd, bins=20, histtype='step', label='rnd')
    plt.legend(loc='best')
    plt.xlabel("Difference to float ped-sub ADC")
    plt.ylabel("N")
    plt.show()


if __name__ == '__main__':
    main()
