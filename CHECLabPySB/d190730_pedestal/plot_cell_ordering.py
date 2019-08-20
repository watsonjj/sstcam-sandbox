from CHECLabPy.plotting.setup import Plotter
from CHECLabPy.core.io import HDF5Reader
from CHECLabPySB import get_data, get_plot
from CHECLabPySB.d190730_pedestal import Lab_bright, d20190614_pedestal_3, setup_cells
from target_calib import PedestalArrayReader
import numpy as np
import pandas as pd
from tqdm import tqdm
from IPython import embed


def main():
    path = Lab_bright().reduced_cell_info
    # path = d20190614_pedestal_3().reduced_cell_info
    with HDF5Reader(path) as r:
        df = r.read("data")
        df = setup_cells(df)

    df = df.groupby("iev").first().reset_index()

    embed()


if __name__ == '__main__':
    main()