from CHECLabPy.core.io import TIOReader
from CHECLabPySB import get_astri_2019
from tqdm import trange
import numpy as np
from matplotlib import pyplot as plt

path = get_astri_2019("d2019-06-14_pedestal/Run13794_r0.tio")
reader = TIOReader(path)
dt = np.zeros(reader.n_events-1)
for iev in trange(1, reader.n_events):
    dt[iev-1] = (reader[iev].t_cpu - reader[iev-1].t_cpu).value

plt.hist(dt, bins=100)
plt.yscale("log")