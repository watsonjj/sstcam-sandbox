from sstcam_sandbox import get_data
from sstcam_sandbox.d190823_pedestal_residuals.cell_operations import setup_cells
import numpy as np
import pandas as pd
import dask
import dask.array as da
import dask.dataframe as dd
from CHECLabPy.core.io import TIOReader, HDF5Writer
from CHECLabPy.calib.waveform import WaveformCalibrator
from tqdm import tqdm
from IPython import embed


class DaskTIO:
    def __init__(self, reader, wf_calib):
        self.reader = reader
        self.n_pixels = 64#reader.n_pixels
        self.n_samples = reader.n_samples
        self.n_rows = self.n_pixels * self.n_samples
        self.shape = (5, self.n_pixels, self.n_samples)
        self.dtype = reader.dtype

        self.wf_calib = wf_calib

        self.ipix, self.isam = np.indices((self.n_pixels, self.n_samples))
        # self.ipix = self.ipix.ravel()
        # self.isam = self.isam.ravel()

        self.pbar = tqdm(total=reader.n_events)

    def get_event(self, iev):
        r0 = self.reader[iev][:self.n_pixels]
        fci = r0.first_cell_id
        fci = np.full(r0.shape, fci, dtype=np.uint16)
        iev = np.full(r0.shape, iev, dtype=np.uint16)
        self.pbar.update(1)
        return np.stack([r0, fci, iev, self.ipix, self.isam])

    def get_file_df(self):
        delayed_event = dask.delayed(self.get_event, pure=True)
        arrays = [
            da.from_delayed(
                delayed_event(iev), dtype=self.dtype, shape=self.shape
            )
            for iev in range(self.reader.n_events)
        ]
        stack = np.rollaxis(da.stack(arrays, axis=0), 1)
        stack = stack.reshape((stack.shape[0], np.prod(stack.shape[1:]))).T
        df = dd.from_dask_array(
            stack,
            columns=["r0", "fci", "iev", "ipix", "isam"]
        )
        df = setup_cells(df)
        return df


def main():
    input_path = "/Users/Jason/Downloads/tempdata/Run06136_r0.tio"
    pedestal_path = "/Users/Jason/Downloads/tempdata/Run06136_ped.tcal"
    max_events = None

    reader = TIOReader(input_path, max_events=max_events)
    wf_calib = WaveformCalibrator(
        pedestal_path, reader.n_pixels, reader.n_samples
    )

    dtio = DaskTIO(reader, wf_calib)
    ddf = dtio.get_file_df()
    # print("here")
    df_0, df_2 = dd.compute(
        ddf.groupby(['ipix', 'fblock', 'fbpisam'])['r0'].std(),
        ddf.groupby(['ipix', 'fci', 'fbpisam'])['r0'].std(),
    )
    embed()


if __name__ == '__main__':
    main()
