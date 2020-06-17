import numpy as np
from sstcam_sandbox import get_data, get_plot
from CHECLabPy.core.io import HDF5Reader
from IPython import embed


def process(path, output_dir):
    with HDF5Reader(path) as reader:
        df = reader.read('data')

    dtack = []
    stale = []
    fci = []
    for _, group in df.groupby("ipath"):
        dtack.append(np.diff(group['tack']))
        stale.append(group['stale'][1:])
        fci.append(group['fci'][1:])
    dtack = np.concatenate(dtack)
    stale = np.concatenate(stale).astype(np.bool)
    fci = np.concatenate(fci)

    istale = np.where(stale)[0]
    
    embed()

def main():
    path = get_data("d190505_dtack/d2019-05-01_mrk501.h5")
    output_dir = get_plot("d190505_dtack/d2019-05-01_mrk501")
    process(path, output_dir)


if __name__ == '__main__':
    main()
