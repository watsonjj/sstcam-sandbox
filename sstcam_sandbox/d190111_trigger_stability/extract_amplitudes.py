from sstcam_sandbox.d190111_trigger_stability import *
from sstcam_sandbox import get_data, HDF5Writer
from CHECLabPy.core.io import TIOReader
from target_calib import MappingSP, CameraConfiguration
import numpy as np
import pandas as pd
from tqdm import tqdm
from matplotlib import pyplot as plt
from IPython import embed


def obtain_pixel_list(superpixels):
    mapping = CameraConfiguration("1.1.0").GetMapping()
    mappingsp = MappingSP(mapping)
    pix_dict = dict()
    for sp in superpixels.keys():
        pix_dict[sp] = list(mappingsp.GetContainedPixels(sp))
    return pix_dict


def process(readers, output_path, superpixels):
    pix_dict = obtain_pixel_list(superpixels)

    df_list = []
    df_list_sum = []

    desc0 = "Looping over files"
    desc1 = "Looping over events"
    for reader in tqdm(readers, total=len(readers), desc=desc0):
        n_events = reader.n_events
        mapping = reader.tc_mapping
        mappingsp = MappingSP(mapping)

        for wfs in tqdm(reader, total=n_events, desc=desc1):
            iev = wfs.iev
            t_cpu = wfs.t_cpu

            for sp, p in pix_dict.items():
                wfs_pix = wfs[p]

                amplitude = wfs_pix.max(axis=1)
                baseline = wfs_pix[:, :20].mean(axis=1)

                # plt.plot(wfs_pix.T)
                # plt.title("iev = {}".format(iev))
                # plt.ylim((-60, 60))
                # plt.pause(1)
                # plt.cla()

                df_list.append(pd.DataFrame(dict(
                    iev=iev,
                    t_cpu=t_cpu,
                    pixel=p,
                    superpixel=sp,
                    amplitude=amplitude,
                    baseline=baseline,
                )))

                wfs_sum = wfs_pix.sum(0)
                amplitude = wfs_sum.max()
                baseline = wfs_sum[:20].mean()

                df_list_sum.append(pd.DataFrame(dict(
                    iev=iev,
                    t_cpu=t_cpu,
                    superpixel=sp,
                    amplitude=amplitude,
                    baseline=baseline,
                ), index=pd.Index([0])))

    df = pd.concat(df_list, ignore_index=True)
    df_sum = pd.concat(df_list_sum, ignore_index=True)

    with HDF5Writer(output_path) as writer:
        writer.write(data=df)
        writer.write(data_sum=df_sum)
        meta = {"sp{}".format(sp): l for sp, l in superpixels.items()}
        writer.write_metadata(**meta)


def process_file(file):
    readers = file.tio_readers
    name = file.__class__.__name__
    output_path = get_data("d190111_trigger_stability/{}/amplitudes.h5".format(name))
    superpixels = file.spoi
    process(readers, output_path, superpixels)


def main():
    files = [
        d190111(),
        # d190115_1mAcut(),
        # d190115_1mAcut_12h(),
    ]
    [process_file(file) for file in files]


if __name__ == '__main__':
    main()
