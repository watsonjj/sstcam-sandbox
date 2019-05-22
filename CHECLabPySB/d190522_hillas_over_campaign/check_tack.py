from CHECLabPy.plotting.setup import Plotter
from CHECLabPy.core.io import HDF5Reader
from CHECLabPySB import get_astri_2019, get_plot
import numpy as np
from os.path import join
from IPython import embed


class TackPlotter(Plotter):
    def add(self, values, label):
        self.ax.hist(
            values, bins='auto', density=True,
            histtype='step', label=label
        )

    def finish(self):
        self.ax.set_xlabel("TACK (ns)")
        self.ax.set_ylabel("Density")


def main():
    path = get_astri_2019("d2019-05-02_mrk421/Run12913_hillas.h5")
    with HDF5Reader(path) as reader:
        t_tack, length = reader.select_columns('data', ['t_tack', 'length'])

    tack = t_tack.values.astype(np.int)
    notzero = tack != 0
    tack = tack[notzero]
    length = length[notzero]
    mask = (length > 2.2) & (length < 2.4)
    tack_noisy = tack[mask]

    dtack = np.diff(tack)
    dtack_noisy = np.diff(tack_noisy)

    # embed()

    output_dir = get_plot("d190522_hillas_over_campaign")

    p_tack = TackPlotter()
    p_tack.add(dtack, label="All")
    # p_tack.add(dtack_noisy, label="Noisy Events")
    p_tack.save(join(output_dir, "dtack.pdf"))


if __name__ == '__main__':
    main()
