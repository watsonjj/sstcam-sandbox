import numpy as np
import os
from tqdm import tqdm
from scipy import interpolate
from scipy.ndimage import correlate1d
from matplotlib import pyplot as plt, animation
from matplotlib.ticker import MultipleLocator
from CHECLabPy.plotting.setup import Plotter
from CHECLabPy.plotting.waveform import WaveformPlotter
from IPython import embed


def get_reference():
    path = "/Users/Jason/Software/CHECLabPy_sandbox/cross_correlation/reference_lei.txt"
    file = np.loadtxt(path)
    refx = file[:, 0]
    refy = file[:, 1] - file[:, 1][0]
    f = interpolate.interp1d(refx, refy, kind=3)
    x = np.linspace(0, 77e-9, 76)
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
    y = y / correlate1d(y_1pe, y).max()

    return y


def get_wf():
    path = "/Users/Jason/Software/CHECLabPy_sandbox/cross_correlation/wf_600mV.npy"
    wf = np.load(path)
    return wf


def scipy_cc(wf):
    return correlate1d(wf, get_reference())


class CrossCorrelation:
    def __init__(self, n_samples):
        self.reference_pulse = get_reference()
        self.n_samples = n_samples
        self.ref_pad = np.pad(self.reference_pulse, n_samples, 'constant')
        self.ref_t_start = self.ref_pad.size // 2
        self.ref_t_end = self.ref_t_start + n_samples

    def ref_t(self, t):
        if t > self.n_samples:
            raise IndexError
        start = self.ref_t_start - t
        end = self.ref_t_end - t
        return self.ref_pad[start:end]

    def multiply(self, waveform, t):
        return waveform * self.ref_t(t)

    def cc_point(self, waveform, t):
        return np.sum(self.multiply(waveform, t))

    def cc(self, waveform):
        result = np.zeros(self.n_samples)
        for t in range(self.n_samples):
            result[t] = self.cc_point(waveform, t)
        return result


class Scatter(Plotter):
    def __init__(self, title="", x_label="", y_label=""):
        super().__init__()
        self.title = title
        self.x_label = x_label
        self.y_label = y_label

    def add(self, x, data, label=""):
        if x is None:
            self.ax.plot(data, label=label)
        else:
            self.ax.plot(x, data, label=label)

    def finish(self):
        self.ax.set_title(self.title)
        self.ax.set_xlabel(self.x_label)
        self.ax.set_ylabel(self.y_label)


class CCAnimated(WaveformPlotter):
    def __init__(self):
        super().__init__()

        figsize = self.figsize()
        figsize[1] *= 3
        self.fig = plt.figure(figsize=figsize)
        self.ax1 = self.fig.add_subplot(3, 1, 1)
        self.ax1t = self.ax1.twinx()
        self.ax2 = self.fig.add_subplot(3, 1, 2)
        self.ax3 = self.fig.add_subplot(3, 1, 3)

        self.n_samples = None
        self.source = None

    @staticmethod
    def align_yaxis(ax1, ax2):
        """Align zeros of the two axes, zooming them out by same ratio"""
        axes = np.array([ax1, ax2])
        extrema = np.array([ax.get_ylim() for ax in axes])
        tops = extrema[:, 1] / (extrema[:, 1] - extrema[:, 0])
        # Ensure that plots (intervals) are ordered bottom to top:
        if tops[0] > tops[1]:
            axes, extrema, tops = [a[::-1] for a in (axes, extrema, tops)]

        # How much would the plot overflow if we kept current zoom levels?
        tot_span = tops[1] + 1 - tops[0]

        extrema[0, 1] = extrema[0, 0] + tot_span * (
                    extrema[0, 1] - extrema[0, 0])
        extrema[1, 0] = extrema[1, 1] + tot_span * (
                    extrema[1, 0] - extrema[1, 1])
        [axes[i].set_ylim(*extrema[i]) for i in range(2)]

    def plot(self, wf, python_cc):
        self.n_samples = wf.size

        ref_0 = python_cc.ref_t(0)
        multiply_0 = python_cc.multiply(wf, 0)
        mask = np.ones(self.n_samples)
        cc = np.ma.zeros(self.n_samples)
        cc.mask = mask
        cc.mask[-1] = 0

        l_wf = self.ax1.plot(wf, color='blue', label="Waveform")[0]
        l_ref = self.ax1t.plot(ref_0, color='green', label="Reference")[0]
        l_multiply = self.ax2.plot(multiply_0)[0]
        l_cc = self.ax3.plot(cc)[0]

        l_tline = self.ax3.axvline(0, c='red')

        self.align_yaxis(self.ax1, self.ax1t)

        # self.ax1.legend(loc="upper right")
        self.ax1.set_title("Waveforms")
        self.ax2.set_title("Multiply")
        self.ax3.set_title("Cross-correlation")
        self.ax1.set_ylabel("Waveform Amplitude (mV)", color='blue')
        self.ax1t.set_ylabel("Reference Amplitude", color='green')
        self.ax2.set_ylabel("Amplitude (mV)")
        self.ax3.set_ylabel("Amplitude (mV ns)")
        self.ax3.set_xlabel("Time (ns)")
        self.ax1.xaxis.set_major_locator(MultipleLocator(16))
        self.ax2.xaxis.set_major_locator(MultipleLocator(16))
        self.ax3.xaxis.set_major_locator(MultipleLocator(16))
        self.ax1.tick_params(axis='y', labelcolor='blue')
        self.ax1t.tick_params(axis='y', labelcolor='green')

        self.ax1t.relim()
        self.ax1t.autoscale_view()

        self.fig.tight_layout()

        def animation_generator():
            for t in range(self.n_samples):
                ref = python_cc.ref_t(t)
                multiply = python_cc.multiply(wf, t)
                cc[t] = python_cc.cc_point(wf, t)
                cc.mask[t] = 0

                l_ref.set_ydata(ref)
                l_multiply.set_ydata(multiply)
                l_cc.set_ydata(cc)
                l_tline.set_xdata(t)

                self.ax2.relim()
                self.ax2.autoscale_view()
                self.ax3.relim()
                self.ax3.autoscale_view()

                yield

        self.source = animation_generator()

    def save(self, output_path):
        with tqdm(total=self.n_samples, desc="Creating animation") as pbar:
            def animate(_):
                pbar.update(1)
                next(self.source)

            anim = animation.FuncAnimation(self.fig, animate,
                                           frames=self.n_samples-1,
                                           interval=100)
            anim.save(output_path)
        print("Created animation: {}".format(output_path))


class CCPlot(WaveformPlotter):
    def __init__(self):
        super().__init__()

        figsize = self.figsize()
        figsize[1] *= 3
        self.fig = plt.figure(figsize=figsize)
        self.ax1 = self.fig.add_subplot(3, 1, 1)
        self.ax1t = self.ax1.twinx()
        self.ax2 = self.fig.add_subplot(3, 1, 2)
        self.ax3 = self.fig.add_subplot(3, 1, 3)

        self.n_samples = None
        self.source = None

    @staticmethod
    def align_yaxis(ax1, ax2):
        """Align zeros of the two axes, zooming them out by same ratio"""
        axes = np.array([ax1, ax2])
        extrema = np.array([ax.get_ylim() for ax in axes])
        tops = extrema[:, 1] / (extrema[:, 1] - extrema[:, 0])
        # Ensure that plots (intervals) are ordered bottom to top:
        if tops[0] > tops[1]:
            axes, extrema, tops = [a[::-1] for a in (axes, extrema, tops)]

        # How much would the plot overflow if we kept current zoom levels?
        tot_span = tops[1] + 1 - tops[0]

        extrema[0, 1] = extrema[0, 0] + tot_span * (
                    extrema[0, 1] - extrema[0, 0])
        extrema[1, 0] = extrema[1, 1] + tot_span * (
                    extrema[1, 0] - extrema[1, 1])
        [axes[i].set_ylim(*extrema[i]) for i in range(2)]

    def plot(self, wf, python_cc):
        self.n_samples = wf.size

        cc_result = python_cc.cc(wf)
        t = np.argmax(cc_result)
        ref = python_cc.ref_t(t)
        multiply = python_cc.multiply(wf, t)

        self.ax1.plot(wf, color='blue', label="Waveform")
        self.ax1t.plot(ref, color='green', label="Reference")
        self.ax2.plot(multiply)
        self.ax3.plot(cc_result)

        l_tline = self.ax3.axvline(t, c='red')

        self.align_yaxis(self.ax1, self.ax1t)

    def finish(self):
        self.ax1.set_title("Waveforms")
        self.ax2.set_title("Multiply")
        self.ax3.set_title("Cross-correlation")
        self.ax1.set_ylabel("Waveform Amplitude (mV)", color='blue')
        self.ax1t.set_ylabel("Reference Amplitude", color='green')
        self.ax2.set_ylabel("Amplitude (mV)")
        self.ax3.set_ylabel("Amplitude (mV ns)")
        self.ax3.set_xlabel("Time (ns)")
        self.ax1.xaxis.set_major_locator(MultipleLocator(16))
        self.ax2.xaxis.set_major_locator(MultipleLocator(16))
        self.ax3.xaxis.set_major_locator(MultipleLocator(16))
        self.ax1.tick_params(axis='y', labelcolor='blue')
        self.ax1t.tick_params(axis='y', labelcolor='green')

        self.ax1t.relim()
        self.ax1t.autoscale_view()

        self.fig.tight_layout()


def main():
    wf = get_wf()
    n_samples = wf.size
    # small_pulse = np.pad(wf[20:], (0, n_samples), 'constant')[:n_samples] * 0.5
    # small_pulse = np.pad(wf, (15, 0), 'constant')[:n_samples] * 0.5
    # wf += small_pulse
    # wf /= 2

    python_cc = CrossCorrelation(n_samples)

    scipy_cc_result = scipy_cc(wf)
    python_cc_result = python_cc.cc(wf)

    t_max = np.argmax(python_cc_result)
    val_max = python_cc.cc_point(wf, t_max)
    ref_max = python_cc.ref_t(t_max)
    ref_max_enlarged = ref_max / np.trapz(ref_max) * val_max
    multiply_max = python_cc.multiply(wf, t_max)

    output_dir = os.path.abspath(os.path.dirname(__file__))

    p_reference = WaveformPlotter("Reference Pulse")
    p_reference.add(None, ref_max, "Reference")
    p_reference.save(os.path.join(output_dir, "reference.pdf"))

    p_cc_comparison = WaveformPlotter("CC Comparison")
    p_cc_comparison.add(None, scipy_cc_result, "SciPy")
    p_cc_comparison.add(None, python_cc_result, "Python")
    p_cc_comparison.add_legend()
    p_cc_comparison.save(os.path.join(output_dir, "cc_comparison.pdf"))

    p_waveforms = WaveformPlotter("Waveform Stages")
    p_waveforms.add(None, wf, "Waveform")
    p_waveforms.add(None, ref_max_enlarged, "Reference Scaled")
    # p_waveforms.add(None, multiply_max, "Multiplied")
    p_waveforms.add_legend()
    p_waveforms.save(os.path.join(output_dir, "waveforms.pdf"))

    p_animation = CCAnimated()
    p_animation.plot(wf, python_cc)
    p_animation.save(os.path.join(output_dir, "cross_correlation.mp4"))

    p_result = CCPlot()
    p_result.plot(wf, python_cc)
    p_result.save(os.path.join(output_dir, "cross_correlation.pdf"))


if __name__ == '__main__':
    main()
