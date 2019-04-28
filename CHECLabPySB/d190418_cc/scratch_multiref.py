from CHECLabPy.core.io import TIOReader
import numpy as np
from numba import njit, prange, float32, float64, guvectorize
from scipy.ndimage import correlate1d
from scipy import interpolate

path = "/Users/Jason/Software/CHECLabPy/refdata/Run17473_r1.tio"
r = TIOReader(path)
ref_path = r.reference_pulse_path
wf = r[0]


def get_ref_pulse(path):
    file = np.loadtxt(path)
    time_slice = 1E-9
    refx = file[:, 0]
    refy = file[:, 1]
    f = interpolate.interp1d(refx, refy, kind=3)
    max_sample = int(refx[-1] / time_slice)
    x = np.linspace(0, max_sample * time_slice, max_sample + 1)
    y = f(x)

    # Put pulse in center so result peak time matches with input peak
    pad = y.size - 2 * np.argmax(y)
    if pad > 0:
        y = np.pad(y, (pad, 0), mode='constant')
    else:
        y = np.pad(y, (0, -pad), mode='constant')

    # Create 1p.e. pulse shape
    y_1pe = y / np.trapz(y)

    # Make maximum of cc result == 1
    y_pad = np.pad(y, y.size, 'constant')
    y = y / correlate1d(y_1pe[None, :], y_pad).max()
    return y

def get_ref_pulse_bare(path):
    file = np.loadtxt(path)
    time_slice = 1E-9
    refx = file[:, 0]
    refy = file[:, 1]
    f = interpolate.interp1d(refx, refy, kind=3)
    max_sample = int(refx[-1] / time_slice)
    x = np.linspace(0, max_sample * time_slice, max_sample + 1)
    y = f(x)

    # Create 1p.e. pulse shape
    y_1pe = y / np.trapz(y)

    # Make maximum of cc result == 1
    y = y / correlate1d(y_1pe, y).max()
    return y


@njit([
    float64[:, :](float64[:, :], float64[:, :]),
    float64[:, :](float32[:, :], float64[:, :]),
], parallel=True, nogil=True)
def cross_correlate_1(w, ref):
    n_pixels, n_samples = w.shape
    n_ref_pix, n_ref_samples = ref.shape
    n_ref = n_ref_samples
    cc_res = np.zeros((n_pixels, n_samples+n_ref))
    for ipix in prange(n_pixels):
        ref_pix = ref[ipix] if n_ref_pix == n_pixels else ref[0]
        for n in prange(n_samples+n_ref):
            for m in prange(n - n_samples, n):
                iref = n_ref - n + m
                if 0 <= m < n_samples and 0 <= iref < n_ref:
                    cc_res[ipix, n] += w[ipix, m] * ref_pix[iref]
    return cc_res


@njit([
    float64[:, :](float64[:, :], float64[:, :]),
    float64[:, :](float32[:, :], float64[:, :]),
], parallel=True, nogil=True)
def cross_correlate_2(w, ref):
    n_pixels, n_samples = w.shape
    n_ref_pix, n_ref_samples = ref.shape
    ref_t_start = n_ref_samples // 2
    ref_t_end = ref_t_start + n_samples
    cc_res = np.zeros((n_pixels, n_samples))
    for ipix in prange(n_pixels):
        ref_pix = ref[ipix] if n_ref_pix == n_pixels else ref[0]
        for t in range(n_samples):
            start = ref_t_start - t
            end = ref_t_end - t
            cc_res[ipix, t] = np.sum(w[ipix] * ref_pix[start:end])
    return cc_res


@njit([
    float64[:, :](float64[:, :], float64[:, :]),
    float64[:, :](float32[:, :], float64[:, :]),
], parallel=True, nogil=True)
def cross_correlate_3(w, ref):
    n_pixels, n_samples = w.shape
    n_ref_pix, n_ref_samples = ref.shape
    ref_pad = np.zeros((n_ref_pix, n_ref_samples + n_samples * 2))
    ref_pad[:, n_samples:n_samples+n_ref_samples] = ref
    cc_res = np.zeros((n_pixels, n_samples))
    for ipix in prange(n_pixels):
        ref_pix = ref_pad[ipix] if n_ref_pix == n_pixels else ref_pad[0]
        ref_t_start = np.argmax(ref_pix)
        for t in prange(n_samples):
            start = ref_t_start - t
            end = start + n_samples
            cc_res[ipix, t] = np.sum(w[ipix] * ref_pix[start:end])
    return cc_res


@guvectorize(
    [
        (float64[:], float64[:], float64[:]),
        (float32[:], float64[:], float64[:]),
    ],
    '(s),(r)->(s)',
    nopython=True, target='parallel'
)
def cross_correlate_4(w, ref, ret):
    n_samples = w.size
    ref_pad = np.zeros(ref.size + n_samples * 2)
    ref_pad[n_samples:n_samples+ref.size] = ref
    ref_t_start = ref_pad.argmax()
    for t in range(n_samples):
        start = ref_t_start - t
        end = start + n_samples
        ret[t] = np.sum(w * ref_pad[start:end])


reference_pulse = get_ref_pulse(ref_path)
reference_pulse2 = np.pad(reference_pulse, wf.shape[-1], 'constant')
reference_pulse3 = get_ref_pulse_bare(ref_path)

reference_pulse = reference_pulse[None, :]
reference_pulse2 = reference_pulse2[None, :]
reference_pulse3 = reference_pulse3[None, :]

# n_pixels, n_samples = wf.shape
# reference_pulse = np.tile(reference_pulse, (n_pixels, 1)) * (np.arange(2048)[:, None] + 1)
# reference_pulse2 = np.tile(reference_pulse2, (n_pixels, 1)) * (np.arange(2048)[:, None] + 1)
# reference_pulse3 = np.tile(reference_pulse3, (n_pixels, 1)) * (np.arange(2048)[:, None] + 1)

# cs = correlate1d(wf, reference_pulse, mode='constant')[0]
c1 = cross_correlate_1(wf, reference_pulse)
c2 = cross_correlate_2(wf, reference_pulse2)
c3 = cross_correlate_3(wf, reference_pulse3)
c4 = cross_correlate_4(wf, reference_pulse3)

assert np.allclose(c2, c3)
assert np.allclose(c3, c4)
assert np.allclose(c2, c4)

# plt.plot(cs)
# plt.plot(c1)
# plt.plot(c2)
# plt.plot(c3)
#
# %timeit correlate1d(wf, reference_pulse, mode='constant')
# %timeit cross_correlate_1(wf, reference_pulse)
# %timeit cross_correlate_2(wf, reference_pulse2)
# %timeit cross_correlate_3(wf, reference_pulse3)
# %timeit cross_correlate_4(wf, reference_pulse3)
