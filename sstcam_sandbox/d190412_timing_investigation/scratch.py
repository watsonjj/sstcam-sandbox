import numpy as np
import numpy.polynomial.polynomial as npp
import pandas as pd
from scipy.stats import norm
from scipy.signal import butter, filtfilt
from numba import njit, prange, guvectorize, float64, float32, int64


def camera_waveforms(t_pulse, noise_offset, noise_std):
    n_samples = 96
    pulse_sigma = 6
    r = np.random.RandomState(1)

    x = np.linspace(0, n_samples, n_samples+1)

    y_pulse = norm.pdf(x, t_pulse, pulse_sigma)
    y_pulse /= y_pulse.max()
    y_noise = r.normal(noise_offset, noise_std, (1000, x.size))

    y = y_pulse + y_noise

    return x, y


def calculate_t1(x, wf):
    return np.average(np.tile(x, (wf.shape[0], 1)), weights=wf, axis=1)

@guvectorize(
    [(float64[:], float64[:], float64[:])],
    '(s),(s)->()',
    nopython=True,
)
def calculate_t2(x, wf, ret):
    n_samples = wf.size
    peakpos = np.argmax(wf)
    start = peakpos - 4
    end = peakpos + 4
    num = 0
    den = 0
    for sample in prange(start, end):
        if 0 <= sample < n_samples:
            num += wf[sample] * x[sample]
            den += wf[sample]
    ret[0] = num / den


@guvectorize(
    [
        (float64[:], float64[:], float64[:]),
        (int64[:], float64[:], float64[:]),
        (float64[:], float32[:], float64[:]),
        (int64[:], float32[:], float64[:]),
    ],
    '(s),(s)->()',
    nopython=True,
)
def calculate_t3(x, wf, ret):
    peakpos = np.argmax(wf)
    y0 = wf[peakpos-1]
    y1 = wf[peakpos]
    y2 = wf[peakpos+1]
    a = y0 - y2
    b = y0 - 2 * y1 + y2
    xm = 0.5 * a / b
    # ym = y1 - 0.25 * (y0 - y2) * xm
    ret[0] = xm + x[peakpos]

def calculate_t4(x, wf):
    return x[np.argmax(wf, 1)]

def calculate_t5(x, wf):
    sample_i = np.indices(wf.shape)[-1]
    peakpos = np.argmax(wf, axis=1).astype(np.intp)
    t = np.zeros(wf.shape[0])
    for i, w in enumerate(wf):
        start = peakpos[i] - 3
        end = peakpos[i] + 3
        c = npp.polyfit(x[start:end], w[start:end], 2)
        dc = npp.polyder(c)
        t[i] = -dc[0]/dc[1]
    return t

def calculate_t6(x, wf):
    filter_ = butter(4, 0.1)
    filtered = filtfilt(*filter_, wf)
    return calculate_t2(x, filtered)

def calculate_t7(x, wf):
    filter_ = butter(4, 0.1)
    filtered = filtfilt(*filter_, wf)
    return calculate_t3(x, filtered)

def calculate_t8(x, wf):
    filter_ = butter(4, 0.1)
    filtered = filtfilt(*filter_, wf)
    return calculate_t4(x, filtered)

def calculate_rmse(x, wf, t_pulse):
    algorithms = dict(
        t1=calculate_t1,
        t2=calculate_t2,
        t3=calculate_t3,
        t4=calculate_t4,
        # t5=calculate_t5,
        t6=calculate_t6,
        t7=calculate_t7,
        t8=calculate_t8,
    )
    result = dict()
    for key, alg in algorithms.items():
        t = alg(x, wf)
        rmse = np.sqrt(np.sum((t - t_pulse)**2)/t.size)
        result[key] =rmse
    return result


t_pulse = 62.25
noise_offset = 0
d_list = []
for noise_std in np.linspace(0, 0.8, 100):
    x, y = camera_waveforms(t_pulse, noise_offset, noise_std)
    rmse_dict = calculate_rmse(x, y, t_pulse)

    d_list.append(dict(
        t_pulse=t_pulse,
        noise_offset=noise_offset,
        noise_std=noise_std,
        **rmse_dict,
    ))

df = pd.DataFrame(d_list)
for t in rmse_dict.keys():
    plt.plot(df['noise_std'].values, df[t].values, label=t)
plt.gca().legend()
