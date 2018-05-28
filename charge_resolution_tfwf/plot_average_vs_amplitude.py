import argparse
from argparse import ArgumentDefaultsHelpFormatter as Formatter
import numpy as np
import os
from CHECLabPy.plotting.waveform import WaveformPlotter
from CHECLabPy.plotting.setup import Plotter
from CHECLabPy.waveform_reducers.cross_correlation import CrossCorrelation
from IPython import embed


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

    def add_saturation_region(self, x1, x2):
        self.ax.axvspan(x1, x2, color='red', alpha=0.5, ec=None)

    def finish(self):
        # self.ax.set_title(self.title)
        self.ax.set_xlabel(self.x_label)
        self.ax.set_ylabel(self.y_label)


class WaveformPlotterDual(WaveformPlotter):
    def __init__(self, title="", units="", tunits="ns", talk=False):
        super().__init__(title, units, tunits, talk)
        # self.axt = self.ax.twinx()

    def add_reference_pulse(self, wf):
        self.ax.plot(wf, color='black')

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

    def finish(self):
        super().finish()
        # y_label = "Amplitude"
        # if self.units:
        #     y_label += " ({})".format(self.units)
        # self.ax.set_ylabel(y_label, color='blue')

        # self.align_yaxis(self.ax, self.axt)
        # self.axt.set_ylabel("Reference Amplitude", color='black')
        # self.ax.tick_params(axis='y', labelcolor='blue')
        # self.axt.tick_params(axis='y', labelcolor='black')
        # self.axt.relim()
        # self.axt.autoscale_view()
        #
        # self.fig.tight_layout()


def main():
    description = ''
    parser = argparse.ArgumentParser(description=description,
                                     formatter_class=Formatter)
    parser.add_argument('-f', '--file', dest='input_path', action='store',
                        required=True,
                        help='path to the extract_average_vs_amplitude '
                             'numpy file')
    parser.add_argument('-o', '--output', dest='output_dir',
                        action='store', required=True,
                        help='directory to store the plots')
    args = parser.parse_args()

    input_path = args.input_path
    output_dir = args.output_dir

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print("Created directory: {}".format(output_dir))

    ref_output_dir = os.path.join(output_dir, "reference_pulses")
    if not os.path.exists(ref_output_dir):
        os.makedirs(ref_output_dir)
        print("Created directory: {}".format(ref_output_dir))

    p_average = WaveformPlotter("Average WF Over Module for each Input Amplitude", "mV")
    p_cc_average = WaveformPlotter("Average Cross-Correlated WF", "mV ns")
    p_ref = WaveformPlotterDual("Reference Pulse")
    p_fwhm = Scatter("FWHM", "Input Amplitude (mV)", "FWHM (ns)")
    p_rise_time = Scatter("Rise Time", "Input Amplitude (mV)", "Rise Time (ns)")
    p_charge = Scatter("Charge", "Input Amplitude (mV)", "Charge (mV ns)")

    average_wf_dict = np.load(input_path)
    amplitudes_str = np.array(average_wf_dict.keys())
    sort = np.argsort([float(a) for a in amplitudes_str])
    sorted_dict = {a: average_wf_dict[a] for a in amplitudes_str[sort]}
    amplitudes = amplitudes_str.astype(np.float)[sort]
    n_amps = len(average_wf_dict.keys())
    n_pixels = 1
    n_samples = average_wf_dict[amplitudes_str[0]].size

    cc = CrossCorrelation(n_pixels, n_samples)#, reference_pulse_path = "/Users/Jason/Software/CHECLabPy/CHECLabPy/data/checs_reference_pulse.txt")

    fwhm = np.zeros(n_amps)
    rise_time = np.zeros(n_amps)
    charge = np.zeros(n_amps)
    cc_ref = None

    for i, (a_str, wf) in enumerate(sorted_dict.items()):
        a = float(a_str)
        # if a > 1000:
        #     continue
        ccwf = cc._apply_cc(wf)
        x = np.arange(wf.size)
        p_average.add(x, wf, a)
        p_cc_average.add(x, ccwf, a)
        wf_norm = wf / np.max(wf)
        p_ref.add(x, wf_norm, a)
        params = cc.process(wf[None, :])
        fwhm[i] = params['fwhm'][0]
        rise_time[i] = params['tr'][0]
        charge[i] = params['charge'][0]
        if (a > 50) & (cc_ref is None):
            cc_ref = cc.get_reference_pulse_at_t(cc.t_event)
            cc_ref = cc_ref / np.max(cc_ref)

        ref_pulse = wf / np.trapz(wf)
        x_ref_pulse = np.arange(ref_pulse.size) * 1E-9
        ref_save = np.column_stack((x_ref_pulse, ref_pulse))
        ref_output = os.path.join(ref_output_dir, "amplitude_{}.txt".format(a))
        np.savetxt(ref_output, ref_save, fmt='%.5e')
        print("Created reference pulse: {}".format(ref_output))

    p_ref.add_reference_pulse(cc_ref)

    # from IPython import embed
    # embed()

    p_fwhm.add(amplitudes, fwhm)
    p_rise_time.add(amplitudes, rise_time)
    p_charge.add(amplitudes, charge)

    p_fwhm.add_saturation_region(1500, np.max(amplitudes)+10)
    p_rise_time.add_saturation_region(1500, np.max(amplitudes)+10)
    p_charge.add_saturation_region(1500, np.max(amplitudes)+10)

    output_path = os.path.join(output_dir, "average_wfs.pdf")
    # p_average.add_legend()
    p_average.save(output_path)

    output_path = os.path.join(output_dir, "average_cc_wfs.pdf")
    p_cc_average.save(output_path)

    output_path = os.path.join(output_dir, "ref_wfs.pdf")
    p_ref.save(output_path)

    output_path = os.path.join(output_dir, "fwhm.pdf")
    p_fwhm.save(output_path)

    output_path = os.path.join(output_dir, "rise_time.pdf")
    p_rise_time.save(output_path)

    output_path = os.path.join(output_dir, "charge.pdf")
    p_charge.save(output_path)


if __name__ == '__main__':
    main()
