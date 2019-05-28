from CHECLabPySB import get_astri_2019, get_data
from CHECLabPy.core.io import DL1Reader
from os.path import join, dirname, exists, abspath
import pandas as pd
import re
from collections import defaultdict
from IPython import embed


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

    n_investigations = len(runlist_paths)
    mapping = None

    pattern = re.compile(r"(?:.+)/d(?:.+)_(.+)/runlist.txt")

    time = defaultdict(float)

    for iinv, path in enumerate(runlist_paths):
        print(f"PROGRESS: Processing inv {iinv+1}/{n_investigations}")

        if not exists(path):
            raise ValueError(f"Missing runlist file: {path}")

        directory = abspath(dirname(path))
        investigation = directory.split('/')[-1]
        df_runlist = pd.read_csv(path, sep='\t')

        pattern = re.compile(r"(?:.+)/d(?:.+)_(.+)/runlist.txt")
        reg_exp = re.search(pattern, path)
        obj = reg_exp.group(1)

        for _, row in df_runlist.iterrows():
            run = int(row['run'])
            dl1_path = join(directory, f"Run{run:05d}_dl1.h5")

            with DL1Reader(dl1_path) as reader:
                start_time = reader.metadata['start_time']
                end_time = reader.metadata['end_time']
                time[obj] += (end_time - start_time).total_seconds()

    for obj, seconds in time.items():
        hours = seconds / (60 * 60)
        print(f"{obj}: {hours:.4f}")


if __name__ == '__main__':
    main()
