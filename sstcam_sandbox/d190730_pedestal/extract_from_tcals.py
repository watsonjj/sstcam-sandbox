


from CHECLabPy.core.io import HDF5Writer
from sstcam_sandbox import get_data
from sstcam_sandbox.d190730_pedestal import all_files
from target_calib import PedestalArrayReader
import numpy as np
import pandas as pd
from tqdm import tqdm
from IPython import embed


def main():
    d_list = []
    for file in tqdm(all_files):
        tcal_path = file.tcal

        ped_reader = PedestalArrayReader(tcal_path)
        hits_tcal = np.array(ped_reader.GetHits())
        std_tcal = np.array(ped_reader.GetStdDev())

        mask = (hits_tcal < 6) | np.isnan(std_tcal)
        std_tcal = np.ma.masked_array(std_tcal, mask=mask)

        n_noisy = (std_tcal > 5).sum()

        d_list.append(dict(
            name=file.name,
            mean=std_tcal.mean(),
            std=std_tcal.std(),
            min=std_tcal.min(),
            max=std_tcal.max(),
            n_noisy=n_noisy,
        ))

    df = pd.DataFrame(d_list)
    # embed()
    with HDF5Writer(get_data(f"d190730_pedestal/tcal_std.h5")) as w:
        w.write(data=df)


if __name__ == '__main__':
    main()
