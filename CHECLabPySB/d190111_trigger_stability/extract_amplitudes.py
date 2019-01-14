from CHECLabPySB import get_data, HDF5Writer
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


def process(input_paths, output_path, superpixels):
    pix_dict = obtain_pixel_list(superpixels)

    df_list = []
    df_list_sum = []

    desc0 = "Looping over files"
    desc1 = "Looping over events"
    for input_file in tqdm(input_paths, total=len(input_paths), desc=desc0):
        reader = TIOReader(input_file)
        n_events = reader.n_events
        mapping = reader.tc_mapping
        mappingsp = MappingSP(mapping)

        for wfs in tqdm(reader, total=n_events, desc=desc1):
            iev = reader.index
            t_cpu_sec = reader.current_cpu_s
            t_cpu_ns = reader.current_cpu_ns
            t_cpu = pd.to_datetime(
                np.int64(t_cpu_sec * 1E9) + np.int64(t_cpu_ns),
                unit='ns'
            )

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


def main():
    input_paths = [
        "/Volumes/gct-jason/data_checs/d190111_trigger_stability/Run05974_r1.tio",
        "/Volumes/gct-jason/data_checs/d190111_trigger_stability/Run05975_r1.tio",
    ]
    output_path = get_data("d190111_trigger_stability/extract_amplitudes.h5")
    superpixels = {
        151: 'Fast Dropoff',
        101: 'Normal',
        399: 'Dead',
        # 296: 'High',
        145: 'Slow Dropoff',
    }
    process(input_paths, output_path, superpixels)


if __name__ == '__main__':
    main()
