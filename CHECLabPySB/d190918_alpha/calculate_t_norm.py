from CHECLabPy.core.io import HDF5Reader
import astropy.units as u
import numpy as np
import pandas as pd


def caclulate_t_norm(row, index, norm, n_simulated):
    # n_simulated = (row['num_showers'] * row['shower_reuse'])
    mc_index = row['spectral_index']
    e_min = row['energy_range_min'] * u.TeV
    e_max = row['energy_range_max'] * u.TeV
    area = (row['max_scatter_range'] * u.m) ** 2 * np.pi
    solid_angle = (row['max_viewcone_radius'] -
                   row['min_viewcone_radius']) * u.deg

    a = e_min.to_value('TeV')
    b = e_max.to_value('TeV')
    norm_ = norm.to(1 / (u.TeV * u.s * u.m**2 * u.sr)) * u.TeV
    angle = ((1 - np.cos(solid_angle.to_value('rad')))*2*np.pi*u.sr)
    integral = norm_ * (b**(mc_index + 1) - a**(mc_index + 1)) / (mc_index + 1)
    t_norm = (n_simulated / (integral * area * angle)).to_value(u.s)
    return t_norm


path = "/Volumes/gct-jason/astri_onsky_archive/d2019-05-15_simulations/proton.h5"
# path = "/Volumes/gct-jason/astri_onsky_archive/d2019-10-03_simulations/gamma_1deg.h5"
norm = 9.6e-9 / (u.GeV * u.cm ** 2 * u.s * u.sr)
index = -2.7

r = HDF5Reader(path)
df = r.read("mc")
# df_stats = pd.DataFrame(dict(same=df.min() df.max(), df.min(), df.max()])
print(df.iloc[0])

# print(df_stats)
# print(df.max())
n_simulated = (df['num_showers'].values * df['shower_reuse'].values).sum()

for _, row in df.iterrows():
    t_norm = caclulate_t_norm(row, index, norm, n_simulated)
    # print(t_norm)
    # t.append(,)

print(t_norm)
