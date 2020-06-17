from sstcam_sandbox import get_plot
from sstcam_sandbox.plotting.setup import Plotter
from sstcam_sandbox.d181106_tf_investigations import *
from sstcam_sandbox import HDF5Writer, HDF5Reader
from matplotlib.ticker import FuncFormatter
from IPython import embed


class LinePlotter(Plotter):
    def __init__(self, xlabel, ylabel, **kwargs):
        super().__init__(**kwargs)
        self.ax.set_xlabel(xlabel)
        self.ax.set_ylabel(ylabel)

    def plot(self, x, y, label):
        self.ax.plot(x, y, label=label)

    def finish(self):
        super().finish()
        self.add_legend("best")

    def set_logx(self):
        self.ax.set_xscale('log')
        self.ax.get_xaxis().set_major_formatter(
            FuncFormatter(lambda xl, _: '{:g}'.format(xl)))

    def set_logy(self):
        self.ax.set_yscale('log')
        self.ax.get_yaxis().set_major_formatter(
            FuncFormatter(lambda yl, _: '{:g}'.format(yl)))



def main():

    p_measured_mean = LinePlotter("Illumination (p.e.)", "Measured Mean (p.e.)")
    p_measured_res = LinePlotter("Illumination (p.e.)", "Measured Res (p.e.)")
    p_measured_std = LinePlotter("Illumination (p.e.)", "Measured STD (p.e.)")
    p_measured_rms = LinePlotter("Illumination (p.e.)", "Measured RMS (p.e.)")
    p_charge_mean = LinePlotter("Illumination (p.e.)", "Charge Mean (mVns)")
    p_charge_std = LinePlotter("Illumination (p.e.)", "Charge STD (mVns)")
    p_charge_rms = LinePlotter("Illumination (p.e.)", "Charge RMS (mVns)")

    p_measured_close = LinePlotter("Illumination (p.e.)", "Closeness")
    p_measured_std_norm = LinePlotter("Illumination (p.e.)", "Measured STD / Measured Mean")
    p_charge_std_norm = LinePlotter("Illumination (p.e.)", "Charge STD / Charge Mean")

    def process(file, name):
        stats_path = file.stats_path
        poi = file.poi

        with HDF5Reader(stats_path) as reader:
            df = reader.read("data")

        df_p = df.loc[df['pixel'] == poi]

        p_measured_mean.plot(df_p['true'], df_p['measured']['mean'], name)
        p_measured_res.plot(df_p['true'], df_p['measured']['res'], name)
        p_measured_std.plot(df_p['true'], df_p['measured']['std'], name)
        p_measured_rms.plot(df_p['true'], df_p['measured']['rms'], name)
        p_charge_mean.plot(df_p['true'], df_p['charge']['mean'], name)
        p_charge_std.plot(df_p['true'], df_p['charge']['std'], name)
        p_charge_rms.plot(df_p['true'], df_p['charge']['rms'], name)

        y = np.abs(df_p['measured']['mean']/df_p['true'] - 1)
        p_measured_close.plot(df_p['true'], y, name)

        y = df_p['measured']['std'] / df_p['measured']['mean']
        p_measured_std_norm.plot(df_p['true'], y, name)

        y = df_p['charge']['std'] / df_p['charge']['mean']
        p_charge_std_norm.plot(df_p['true'], y, name)

    process(d181010_LabSM_0MHz_100mV_TFNone(), "No TF")
    process(d181010_LabSM_0MHz_100mV_TFPchip(), "TFPCHIP")

    p_measured_mean.plot([0, 2000], [0, 2000], "1-to-1")

    p_measured_mean.set_logx()
    p_measured_res.set_logx()
    p_measured_std.set_logx()
    p_measured_rms.set_logx()
    p_charge_mean.set_logx()
    p_charge_std.set_logx()
    p_charge_rms.set_logx()
    p_measured_close.set_logx()
    p_measured_std_norm.set_logx()
    p_charge_std_norm.set_logx()

    p_measured_mean.set_logy()
    p_measured_res.set_logy()
    p_measured_std.set_logy()
    p_measured_rms.set_logy()
    p_charge_mean.set_logy()
    p_charge_std.set_logy()
    p_charge_rms.set_logy()
    # p_measured_close.set_logy()
    # p_measured_std_norm.set_logy()
    # p_charge_std_norm.set_logy()

    p_measured_mean.save(get_plot("d181106_tf_investigations/stats/measured_mean.pdf"))
    p_measured_res.save(get_plot("d181106_tf_investigations/stats/measured_res.pdf"))
    p_measured_std.save(get_plot("d181106_tf_investigations/stats/measured_std.pdf"))
    p_measured_rms.save(get_plot("d181106_tf_investigations/stats/measured_rms.pdf"))
    p_charge_mean.save(get_plot("d181106_tf_investigations/stats/charge_mean.pdf"))
    p_charge_std.save(get_plot("d181106_tf_investigations/stats/charge_std.pdf"))
    p_charge_rms.save(get_plot("d181106_tf_investigations/stats/charge_rms.pdf"))
    p_measured_close.save(get_plot("d181106_tf_investigations/stats/measured_close.pdf"))
    p_measured_std_norm.save(get_plot("d181106_tf_investigations/stats/measured_std_norm.pdf"))
    p_charge_std_norm.save(get_plot("d181106_tf_investigations/stats/charge_std_norm.pdf"))


if __name__ == '__main__':
    main()
