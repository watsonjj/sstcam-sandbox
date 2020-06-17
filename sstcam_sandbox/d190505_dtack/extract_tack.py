from os.path import dirname, join
import pandas as pd
from sstcam_sandbox import get_data, get_astri_2019
from CHECLabPy.core.io import HDF5Writer, TIOReader
from tqdm import tqdm
import psutil


def process(paths, output_path):
    with HDF5Writer(output_path) as writer:
        for ipath, path in enumerate(paths):
            print(f"File: {ipath+1}/{len(paths)}")
            reader = TIOReader(path)
            n_events = reader.n_events
            for wf in tqdm(reader, total=n_events):
                data = dict(
                    ipath=ipath,
                    iev=wf.iev,
                    tack=wf.t_tack,
                    stale=wf.stale[0],
                    fci=wf.first_cell_id[0],
                )
                writer.append(pd.DataFrame(data, index=[0]))
            print(f"Memory Usage = {psutil.Process().memory_info().rss * 1E-9} GB")


def main():
    runlist_path = get_astri_2019("d2019-05-01_mrk501/runlist.txt")
    directory = dirname(runlist_path)
    df = pd.read_csv(runlist_path, sep='\t')
    paths = [join(directory, f"Run{run:05d}_r1.tio") for run in df['run']]
    output_path = get_data("d190505_dtack/d2019-05-01_mrk501.h5")
    process(paths, output_path)


if __name__ == '__main__':
    main()
