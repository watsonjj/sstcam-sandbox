import argparse
from argparse import ArgumentDefaultsHelpFormatter as Formatter
import numpy as np
import os

from matplotlib.ticker import MultipleLocator

from CHECLabPy.plotting.waveform import WaveformPlotter
from CHECLabPy.plotting.setup import Plotter
from CHECLabPy.waveform_reducers.cross_correlation import CrossCorrelation
from matplotlib.collections import LineCollection


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
    def add_reference_pulse(self, wf):
        self.ax.plot(wf, color='black')


class NormalisedWaveformPlotter(Plotter):
    def __init__(self, title="", units="", tunits="ns", cunits="p.e.", ax=None, talk=False):
        """
        Create a plotter for a waveform

        Parameters
        ----------
        title : str
        units : str
            Y axis units
        tunits : str
            X axis (time) units
        ax : `matplotlib.axes.Axes`
            Optionally place the plot on a pre-existing axes
        talk : bool
            Configure appearance to be appropriate for a presentation
        """
        super().__init__(ax=ax, talk=talk)
        self.title = title
        self.units = units
        self.tunits = tunits
        self.cunits = cunits

        self.x = []
        self.data = []
        self.amplitudes = []

    def add(self, x, data, amplitude):
        data /= np.trapz(data, x)

        self.x.append(x)
        self.data.append(data)
        self.amplitudes.append(amplitude)

    def finish(self):
        sort = np.argsort(self.amplitudes)[::-1]
        self.x = np.array(self.x)[sort]
        self.data = np.array(self.data)[sort]
        self.amplitudes = np.array(self.amplitudes)[sort]

        z = zip(self.x, self.data)
        segments = [np.column_stack([x, y]) for x, y in z]
        lc = LineCollection(segments, lw=0.5)
        lc.set_array(np.array(self.amplitudes))

        self.ax.add_collection(lc)
        self.ax.autoscale()

        cb = self.fig.colorbar(lc)
        cb.set_label('Input Amplitude ({})'.format(self.cunits))

        self.ax.set_title(self.title)
        x_label = "Time"
        if self.tunits:
            x_label += " ({})".format(self.tunits)
        self.ax.set_xlabel(x_label)
        y_label = "Amplitude"
        if self.units:
            y_label += " ({})".format(self.units)
        self.ax.set_ylabel(y_label)
        self.ax.xaxis.set_major_locator(MultipleLocator(16))



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

    p_average = WaveformPlotter("Average WF for each Input Amplitude", "mV")
    p_cc_average = WaveformPlotter("Average Cross-Correlated WF", "mV ns")
    p_ref = WaveformPlotterDual("Reference Pulse")
    p_fwhm = Scatter("FWHM", "Illumination (p.e.)", "FWHM (ns)")
    p_rise_time = Scatter("Rise Time", "Illumination (p.e.)", "Rise Time (ns)")
    p_charge = Scatter("Charge", "Illumination (p.e.)", "Charge (mV ns)")
    p_average_norm = NormalisedWaveformPlotter("Average WF for each Input Amplitude", "mV", cunits="mV")

    average_wf_dict = np.load(input_path)
    average_wf_keys_float = [float(a) for a in average_wf_dict.keys()]
    sorted_key = ["{:.3f}".format(a) for a in np.sort(average_wf_keys_float)]

    n_amps = len(average_wf_dict.keys())
    n_pixels = 1
    n_samples = average_wf_dict[list(average_wf_dict.keys())[0]].size

    cc = CrossCorrelation(n_pixels, n_samples, reference_pulse_path="/Users/Jason/Software/TargetCalib/install/dev/reference_pulse_checs_V1-1-0.cfg")

    illumination = np.zeros(n_amps)
    fwhm = np.zeros(n_amps)
    rise_time = np.zeros(n_amps)
    charge = np.zeros(n_amps)
    cc_ref = None

    for i, ill_str in enumerate(sorted_key):
        ill = float(ill_str)
        if ill > 500:
            continue
        wf = average_wf_dict[ill_str]
        wf_norm = wf / np.max(wf)

        params = cc.process(wf[None, :])
        ccwf = cc._apply_cc(wf)

        x = np.arange(wf.size)
        p_average.add(x, wf, ill_str)
        p_cc_average.add(x, ccwf, ill_str)
        p_ref.add(x, wf_norm, ill_str)
        p_average_norm.add(x, wf, ill)

        illumination[i] = ill
        fwhm[i] = params['fwhm'][0]
        rise_time[i] = params['tr'][0]
        charge[i] = params['charge'][0]
        if (ill > 50) & (cc_ref is None):
            cc_ref = cc.get_reference_pulse_at_t(cc.t_event)
            cc_ref = cc_ref / np.max(cc_ref)

        ref_pulse = wf / np.trapz(wf)
        x_ref_pulse = np.arange(ref_pulse.size) * 1E-9
        ref_save = np.column_stack((x_ref_pulse, ref_pulse))
        fp = "amplitude_{}.txt"
        ref_output = os.path.join(ref_output_dir, fp.format(ill))
        np.savetxt(ref_output, ref_save, fmt='%.5e')
        print("Created reference pulse: {}".format(ref_output))

    p_ref.add_reference_pulse(cc_ref)

    p_fwhm.add(illumination, fwhm)
    p_rise_time.add(illumination, rise_time)
    p_charge.add(illumination, charge)

    p_fwhm.add_saturation_region(1500, np.max(illumination)+10)
    p_rise_time.add_saturation_region(1500, np.max(illumination)+10)
    p_charge.add_saturation_region(1500, np.max(illumination)+10)

    output_path = os.path.join(output_dir, "average_wfs.pdf")
    # p_average.add_legend()
    p_average.save(output_path)

    output_path = os.path.join(output_dir, "average_cc_wfs.pdf")
    p_cc_average.save(output_path)

    output_path = os.path.join(output_dir, "ref_wfs.pdf")
    p_ref.save(output_path)

    output_path = os.path.join(output_dir, "average_wfs_norm.pdf")
    p_average_norm.save(output_path)

    output_path = os.path.join(output_dir, "fwhm.pdf")
    p_fwhm.save(output_path)

    output_path = os.path.join(output_dir, "rise_time.pdf")
    p_rise_time.save(output_path)

    output_path = os.path.join(output_dir, "charge.pdf")
    p_charge.save(output_path)


if __name__ == '__main__':
    main()
