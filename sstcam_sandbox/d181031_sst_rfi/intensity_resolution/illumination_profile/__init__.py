from sstcam_sandbox import get_data, get_plot


class d180907_MC:
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dl1_path = "/Volumes/gct-jason/sim_telarray/d180907_illumination_profile/Run43489_dl1.h5"
        self.illumination_profile_path = get_data("d181031_sst_rfi/intensity_resolution/illumination_profile/d180907_MC.h5")
        self.plot_dir = get_plot("d181031_sst_rfi/intensity_resolution/illumination_profile/d180907_MC")
        self.angular_response_path = get_data("d181031_sst_rfi/intensity_resolution/illumination_profile/transmission_pmma_vs_theta_20150422.dat")
