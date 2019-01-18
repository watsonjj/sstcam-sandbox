# from CHECLabPySB.plotting.setup import Plotter
from CHECLabPySB.d190111_trigger_stability import *
from CHECLabPySB import get_data, get_plot, HDF5Reader
from CHECLabPySB.plotting.camera import CameraImage
from CHECLabPy.core.io import TIOReader
from CHECLabPy.utils.mapping import get_superpixel_mapping
from target_calib import MappingSP, CameraConfiguration
import numpy as np
import pandas as pd
from tqdm import tqdm
from matplotlib import pyplot as plt
from IPython import embed


def hv_file_reader(path):
    hvs = np.zeros((32, 16))
    pattern = 'M:(\d+)\/F\/S:(\d+)\|HV=(\d+)'
    with open(path) as file:
        for line in file:
            regexp = re.search(pattern, line)
            tm = int(regexp.group(1))
            sp = int(regexp.group(2))
            value = int(regexp.group(3))
            hvs[tm, sp] = value
    assert (hvs != 0).all()
    assert hvs.size == 512

    return hvs.ravel()


def process(input_path, output_path, hv_path, event_slice):
    reader = TIOReader(input_path)
    n_events = reader.n_events
    n_pixels = reader.n_pixels
    n_samples = reader.n_samples
    mapping = reader.mapping
    mappingtc = reader.tc_mapping
    mappingsp = MappingSP(mappingtc)

    waveforms = reader[event_slice]

    sp_arr = np.vstack(mapping.groupby("superpixel").pixel.apply(np.array))
    avg_wfs = waveforms[:, sp_arr].mean((0, 2))
    amplitudes = avg_wfs.max(1)

    hvs = hv_file_reader(hv_path)
    hv255 = np.where(hvs == 255)

    df = get_superpixel_mapping(mapping)
    camera = CameraImage.from_mapping(df)
    image = amplitudes
    camera.image = image
    camera.add_colorbar("Superpixel-Waveform Max (mV)")
    camera.highlight_pixels(hv255, 'red')
    camera.save(output_path)

    lt75 = np.where(amplitudes < 75)
    print(lt75)


def process_file(file):
    name = file.__class__.__name__
    input_path = file.tio_paths[0]
    output_path = get_plot("d190111_trigger_stability/{}/disabled_start.pdf".format(name))
    hv_path = file.hv_path
    process(input_path, output_path, hv_path, np.s_[:100])

    name = file.__class__.__name__
    input_path = file.tio_paths[-1]
    output_path = get_plot("d190111_trigger_stability/{}/disabled_end.pdf".format(name))
    hv_path = file.hv_path
    process(input_path, output_path, hv_path, np.s_[-100:])


def main():
    files = [
        d190115_1mAcut(),
    ]
    [process_file(file) for file in files]


if __name__ == '__main__':
    main()
