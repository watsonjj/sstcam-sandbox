from sstcam_sandbox import get_checs
from TargetCalibSB.pedestal import PedestalTargetCalib
from TargetCalibSB import get_cell_ids_for_waveform
from CHECLabPy.core.io import TIOReader
from tqdm import tqdm
from glob import glob


def process(path):
    pedestal_path = path.replace("_r0.tio", "_ped.tcal")
    reader = TIOReader(path)

    pedestal = PedestalTargetCalib(
        reader.n_pixels, reader.n_samples-32, reader.n_cells
    )
    desc = "Generating pedestal"
    for wfs in tqdm(reader, total=reader.n_events, desc=desc):
        if wfs.missing_packets:
            continue
        cells = get_cell_ids_for_waveform(wfs.first_cell_id, reader.n_samples, reader.n_cells)
        wfs = wfs[:, 32:]
        wfs.first_cell_id = cells[32]
        pedestal.add_to_pedestal(wfs, wfs.first_cell_id)
    pedestal.save_tcal(pedestal_path)


def main():
    input_paths = glob(get_checs("d181203_erlangen/pedestal/*.tio"))
    for path in input_paths:
        process(path)


if __name__ == '__main__':
    main()
