import numpy as np
import pandas as pd
from matplotlib import pyplot as plt


t = np.linspace(0, 600, 10000)
y = 0 * np.sin(np.deg2rad(600*t)) + 10*60
t = pd.to_timedelta(t, 's')
t = pd.Timestamp.now() + t

df = pd.DataFrame(dict(t=t, y=y)).set_index("t")

rolling_std = df.rolling('60s', min_periods=5).std()['y'].values
rolling_ste = rolling_std / df.rolling('60s', min_periods=5).count()['y'].values


# plt.plot(t, y, '.')
plt.plot(t, rolling_std, '.')
plt.plot(t, rolling_ste, '.')
