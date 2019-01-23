from CHECLabPySB.d190117_trigger_stability import *
from CHECLabPySB import get_data, HDF5Writer
from CHECLabPy.core.io import TIOReader
from target_calib import MappingSP, CameraConfiguration
import numpy as np
import pandas as pd
from tqdm import tqdm
from matplotlib import pyplot as plt
from IPython import embed


def process(monitor_paths, output_path):

    df_list = []
    iev = 0

    desc0 = "Looping over files"
    desc1 = "Looping over events"
    for path in tqdm(monitor_paths, total=len(monitor_paths), desc=desc0):
        with open(path) as file:
            for line in file:
                if line and line != '\n':
                    try:
                        data = line.replace('\n', '').replace('\t', " ")
                        data = data.split(" ")

                        t_cpu = pd.to_datetime(
                            "{} {}".format(data[0], data[1]),
                            format="%Y-%m-%d %H:%M:%S:%f"
                        )
                        # TODO: store monitor ASCII with UTC timestamps
                        t_cpu = (t_cpu.tz_localize("Europe/Berlin")
                                 .tz_convert("UTC")
                                 .tz_localize(None))

                        if 'Monitoring Event Done' in line:
                            iev += 1
                            continue

                        device = data[2]
                        measurement = data[3]
                        key = device + "_" + measurement
                        if key == "TM_SP_VOLTAGE":
                            imod = int(data[4])
                            sp = imod * 16 + np.arange(16)
                            values = np.array(data[5:21], dtype=np.float)

                            df_list.append(pd.DataFrame(dict(
                                iev=iev,
                                t_cpu=t_cpu,
                                superpixel=sp,
                                hv=values,
                            )))

                    except:
                        pass
                    # except ValueError:
                    #     print("ValueError from line: {}".format(line))
                    # except IndexError:
                    #     print("IndexError from line: {}".format(line))

    df = pd.concat(df_list, ignore_index=True)

    with HDF5Writer(output_path) as writer:
        writer.write(data=df)


def process_file(file):
    monitor_paths = file.monitor_paths
    name = file.__class__.__name__
    output_path = get_data("d190117_trigger_stability/{}/hv.h5".format(name))
    process(monitor_paths, output_path)


def main():
    files = [
        # d190111(),
        # d190118(),
        d190121(),
    ]
    [process_file(file) for file in files]


if __name__ == '__main__':
    main()
