import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from IPython import embed


f_without = "/Volumes/gct-jason/data_checs/dynamicrange_180504/no_tf/spe.h5"
f_with = "/Volumes/gct-jason/data_checs/dynamicrange_180504/spe.h5"

s_without = pd.HDFStore(f_without)
s_with = pd.HDFStore(f_with)

df_p_without = s_without['array_pixel']
df_p_with = s_with['array_pixel']

df_c_without = s_without['array_camera']
df_c_with = s_with['array_camera']

# hist = df_c_without.iloc[0]['hist']
# edges = df_c_without.iloc[0]['edges']
# between = df_c_without.iloc[0]['between']
# fit_x = df_c_without.iloc[0]['fit_x']
# fit = df_c_without.iloc[0]['fit']
# plt.hist(between, bins=edges, weights=hist, histtype='step', color="blue")
# plt.plot(fit_x, fit, color="blue")
#
# hist = df_c_with.iloc[0]['hist']
# edges = df_c_with.iloc[0]['edges']
# between = df_c_with.iloc[0]['between']
# fit_x = df_c_with.iloc[0]['fit_x']
# fit = df_c_with.iloc[0]['fit']
# plt.hist(between, bins=edges, weights=hist, histtype='step', color="red")
# plt.plot(fit_x, fit, color="red")
#
# plt.show()

i = 0
print(i, i%16)
# embed()
#
# for i in range(16):
hist = df_p_without.iloc[i]['hist']
edges = df_p_without.iloc[i]['edges']
between = df_p_without.iloc[i]['between']
fit_x = df_p_without.iloc[i]['fit_x']
fit = df_p_without.iloc[i]['fit']
plt.hist(between, bins=edges, weights=hist, histtype='step', color="blue")
plt.plot(fit_x, fit, color="blue")

hist = df_p_with.iloc[i]['hist']
edges = df_p_with.iloc[i]['edges']
between = df_p_with.iloc[i]['between']
fit_x = df_p_with.iloc[i]['fit_x']
fit = df_p_with.iloc[i]['fit']
plt.hist(between, bins=edges, weights=hist, histtype='step', color="red")
plt.plot(fit_x, fit, color="red")

plt.show()
plt.close('all')