from sstcam_sandbox import get_astri_2019, get_data
from CHECLabPy.core.io import HDF5Reader, HDF5Writer
from os.path import join, dirname, exists, abspath
import pandas as pd


def main():
    base = get_astri_2019("")
    runlist_paths = [
        join(base, "d2019-04-30_cosmicray/runlist.txt"),
        join(base, "d2019-05-01_cosmicray/runlist.txt"),
        join(base, "d2019-05-01_mrk501/runlist.txt"),
        join(base, "d2019-05-02_PG1553+113/runlist.txt"),
        join(base, "d2019-05-02_mrk421/runlist.txt"),
        join(base, "d2019-05-02_mrk501/runlist.txt"),
        join(base, "d2019-05-06_mrk501/runlist.txt"),
        join(base, "d2019-05-07_cosmicray/runlist.txt"),
        join(base, "d2019-05-08_cosmicray/runlist.txt"),
        join(base, "d2019-05-09_mrk421/runlist.txt"),
    ]
    output_path = get_data("d190522_hillas_over_campaign/hillas.h5")

    with HDF5Writer(output_path) as writer:

        n_investigations = len(runlist_paths)
        mapping = None

        for iinv, path in enumerate(runlist_paths):
            print(f"PROGRESS: Processing inv {iinv+1}/{n_investigations}")

            if not exists(path):
                raise ValueError(f"Missing runlist file: {path}")

            directory = abspath(dirname(path))
            investigation = directory.split('/')[-1]
            df_runlist = pd.read_csv(path, sep='\t')

            for _, row in df_runlist.iterrows():
                run = int(row['run'])
                hillas_path = join(directory, f"Run{run:05d}_hillas.h5")

                with HDF5Reader(hillas_path) as reader:
                    if mapping is None:
                        mapping = reader.get_mapping()

                    keys = ['data', 'pointing', 'mc', 'mcheader']
                    for key in keys:
                        if key not in reader.dataframe_keys:
                            continue

                        it = enumerate(reader.iterate_over_chunks(key, 1000))
                        for ientry, df in it:
                            df['iinv'] = iinv
                            df['investigation'] = investigation
                            writer.append(df, key=key)

        writer.add_mapping(mapping)


if __name__ == '__main__':
    main()
