from CHECLabPy.core.io import TIOReader
import numpy as np
from numba import njit, prange, float32, float64, guvectorize, int64
from scipy.ndimage import correlate1d
from scipy import interpolate

path = "/Users/Jason/Software/CHECLabPy/refdata/Run17473_r1.tio"
r = TIOReader(path)
ref_path = r.reference_pulse_path
wf = r[0]

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



# @njit(fastmath=True)
def cross_correlate_pixel(w, ref, res):
    n_samples = w.size
    ref_t_start = np.argmax(ref)
    for t in range(n_samples):
        start = ref_t_start - t
        end = start + n_samples
        res[t] = np.sum(w * ref[start:end])


@njit(parallel=True)
def cross_correlate_camera(w, ref):
    n_pixels, n_samples = w.shape
    n_ref_pix, n_ref_samples = ref.shape
    ref_pad = np.zeros((n_ref_pix, n_ref_samples + n_samples * 2))
    ref_pad[:, n_samples:n_samples+n_ref_samples] = ref
    cc_res = np.zeros((n_pixels, n_samples))
    for ipix in prange(n_pixels):
        ref_pix = ref_pad[ipix] if n_ref_pix == n_pixels else ref_pad[0]
        cross_correlate_pixel(w[ipix], ref_pix, cc_res[ipix])
    return cc_res


# @njit(parallel=True)
# def cross_correlate_global(w, ref):
#     n_pixels, n_samples = w.shape
#     n_ref_pix, n_ref_samples = ref.shape
#     ref_pad = np.zeros((n_ref_pix, n_ref_samples + n_samples * 2))
#     ref_pad[:, n_samples:n_samples+n_ref_samples] = ref
#     cc_res = np.zeros(n_samples)
#     for ipix in prange(n_pixels):
#         ref_pix = ref_pad[ipix] if n_ref_pix == n_pixels else ref_pad[0]
#         ref_t_start = np.argmax(ref_pix)
#         for t in prange(n_samples):
#             start = ref_t_start - t
#             end = start + n_samples
#             cc_res[t] += np.sum(w[ipix] * ref_pix[start:end])
#
#     charge = cc_res.max()
#     peak_index = cc_res.argmax()
#     y0 = cc_res[peak_index - 1]
#     y1 = cc_res[peak_index]
#     y2 = cc_res[peak_index + 1]
#     a = y0 - y2
#     b = y0 - 2 * y1 + y2
#     t = 0.5 * a / b
#     h = y1 - 0.25 * (y0 - y2) * t
#     h_pulse = h - baseline
#     t_pulse = t + peakpos
#     if not 0 <= t_pulse < n_samples:
#         t_pulse_arr[pixel] = np.nan
#         h_pulse_arr[pixel] = np.nan
#         fwhm_arr[pixel] = np.nan
#         rise_time_arr[pixel] = np.nan
#         t_l[pixel] = np.nan
#         t_r[pixel] = np.nan
#         t10[pixel] = np.nan
#         t90[pixel] = np.nan
#         continue
#     i_pulse = int(np.round(t_pulse))
#
#     return cc_res
#
#
# reference_pulse3 = get_ref_pulse_bare(ref_path)
# n_pixels, n_samples = wf.shape
# reference_pulse3 = np.tile(reference_pulse3, (n_pixels, 1)) * (np.arange(2048)[:, None] + 1)
#
#
# c1 = cross_correlate_camera(wf, reference_pulse3)
# c2 = cross_correlate_joint(wf, reference_pulse3)
#
# assert np.allclose(c1, c2)
#
# %timeit cross_correlate_camera(wf, reference_pulse3)
# %timeit cross_correlate_joint(wf, reference_pulse3)
#
