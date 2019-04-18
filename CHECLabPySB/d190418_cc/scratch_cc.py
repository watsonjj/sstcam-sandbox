from CHECLabPy.core.io import TIOReader
from CHECLabPy.waveform_reducers.cross_correlation import CrossCorrelation as CC
import numpy as np
from numba import njit, prange, float32, float64, guvectorize
from scipy.ndimage import correlate1d

path = "/Users/Jason/Software/CHECLabPy/refdata/Run17473_r1.tio"
r = TIOReader(path)
ref_path = r.reference_pulse_path
wf = r[0]
cc = CC(1, 1, reference_pulse_path=ref_path)
reference_pulse = cc.reference_pulse#[36:]


@njit([
    float64[:, :](float64[:, :], float64[:]),
    float64[:, :](float32[:, :], float64[:]),
], parallel=True, nogil=True)
def cross_correlate_1(w, ref):
    n_pixels, n_samples = w.shape
    n_ref = ref.size
    cc_res = np.zeros((n_pixels, n_samples+n_ref))
    for ipix in prange(n_pixels):
        for n in prange(n_samples+n_ref):
            for m in prange(n - n_samples, n):
                iref = n_ref - n_ref - n + m
                if 0 <= m < n_samples and 0 <= iref < n_ref:
                    cc_res[ipix, n] += w[ipix, m] * ref[iref]
    return cc_res


@njit([
    float64[:, :](float64[:, :], float64[:]),
    float64[:, :](float32[:, :], float64[:]),
], parallel=True, nogil=True)
def cross_correlate_2(w, ref):
    n_pixels, n_samples = w.shape
    ref_t_start = ref.size // 2
    ref_t_end = ref_t_start + n_samples
    cc_res = np.zeros((n_pixels, n_samples))
    for ipix in prange(n_pixels):
        for t in range(n_samples):
            start = ref_t_start - t
            end = ref_t_end - t
            cc_res[ipix, t] = np.sum(w[ipix] * ref[start:end])
    return cc_res

reference_pulse2 = np.pad(reference_pulse, wf.shape[-1], 'constant')
c1 = cross_correlate_2(wf, reference_pulse2)[0]
c2 = correlate1d(wf, reference_pulse, mode='constant')[0]

# start = c1.argmax() - c2.argmax()
# end = start + c2.size
# c1 = c1[start:end]

plt.plot(c1)
plt.plot(c2)
# plt.plot(wf[0])
#
# assert np.allclose(c1, c2)
%timeit cross_correlate_1(wf, reference_pulse)
%timeit cross_correlate_2(wf, reference_pulse2)
%timeit correlate1d(wf, reference_pulse, mode='constant')
