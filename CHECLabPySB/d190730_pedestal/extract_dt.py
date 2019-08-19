from CHECLabPy.core.io import TIOReader
from CHECLabPySB.d190730_pedestal import all_files
from tqdm import trange
import numpy as np


def process(input_path, output_path):
    reader = TIOReader(input_path)
    dt = np.zeros(reader.n_events-1)
    for iev in trange(1, reader.n_events):
        dt[iev-1] = (reader[iev].t_cpu - reader[iev-1].t_cpu).value

    np.save(output_path, dt)


def main():
    for file in all_files:
        process(file.r0, file.reduced_dt)


if __name__ == '__main__':
    main()
