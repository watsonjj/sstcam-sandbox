from sstcam_sandbox.d190111_trigger_stability import *
from sstcam_sandbox import get_data, HDF5Writer
import numpy as np
import pandas as pd
from IPython import embed


def read_trigger_file(path):
    sp_data = np.loadtxt(path, skiprows=1)
    superpixels = np.arange(512)

    df_list = []

    for iev, entry in enumerate(sp_data):
        time = pd.to_datetime(entry[0], unit='s')
        counts = entry[1:513]

        df_list.append(pd.DataFrame(dict(
            iev=iev,
            t_cpu=time,
            superpixel=superpixels,
            count=counts,
        )))

    df = pd.concat(df_list, ignore_index=True)
    return df


def process(trigger_path, output_path):
    df = read_trigger_file(trigger_path)
    embed()

    with HDF5Writer(output_path) as writer:
        writer.write(data=df)


def process_file(file):
    trigger_path = file.trigger_path
    name = file.__class__.__name__
    output_path = get_data("d190111_trigger_stability/{}/trigger.h5".format(name))
    process(trigger_path, output_path)


def main():
    files = [
        d190111(),
        # d190115_1mAcut(),
        # d190115_1mAcut_12h(),
    ]
    [process_file(file) for file in files]


if __name__ == '__main__':
    main()
