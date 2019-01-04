from CHECLabPySB.plotting.setup import Plotter
from CHECLabPySB import HDF5Writer
from CHECLabPySB.plotting.camera import CameraImage
from CHECLabPySB.d181021_charge_resolution.illumination_profile import *
import numpy as np
import pandas as pd
from CHECLabPy.core.io import DL1Reader
from matplotlib import pyplot as plt
from numpy.polynomial.polynomial import polyfit, polyval
import os


class IlluminationProfile:
    def __init__(self, angular_response_path):
        self.camera_radius = 1
        self.lightsource_focalplane_seperation = 1.552
        self.pixel_area = 0.00623

        self.angular_response_array = np.loadtxt(angular_response_path,
                                                 unpack=True)

    def distance_to_radial_position(self, x):
        r = self.camera_radius
        dc = self.lightsource_focalplane_seperation
        dz = np.sqrt(x**2 + (dc + r - np.sqrt(r**2 - x**2))**2)
        return dz

    def viewing_angle(self, x):
        r = self.camera_radius
        dz = self.distance_to_radial_position(x)
        theta = np.arcsin(x / dz)
        alpha = np.arcsin(x / r)
        beta = theta + alpha
        return beta

    def viewing_area(self, x):
        beta = self.viewing_angle(x)
        viewing_area = self.pixel_area * np.cos(beta)
        return viewing_area

    def angular_response(self, angle):
        theta = angle * np.pi / 180
        x, y = self.angular_response_array
        response = np.interp(theta, x, y)
        return response

    def angular_response_at_radial_position(self, x):
        angle = self.viewing_angle(x)
        response = self.angular_response(angle)
        return response

    def get_illumination_correction(self, x):
        dc = self.lightsource_focalplane_seperation
        dz = self.distance_to_radial_position(x)
        dz_corr = dc**2 / dz**2

        pa = self.pixel_area
        pz = self.viewing_area(x)
        pz_corr = pz / pa

        ang_corr = self.angular_response_at_radial_position(x)

        correction = dz_corr * pz_corr * ang_corr
        return correction


class PixelScatter(Plotter):
    def __init__(self, illumination_profile):
        super().__init__()

        self.df_list = []

        self.fig = plt.figure(figsize=self.get_figsize())
        self.data_ax = self.fig.add_axes((.1, .3, .8, .6))
        self.data_ax.set_xticklabels([])
        self.res_ax = self.fig.add_axes((.1, .1, .8, .2))

        self.ip = illumination_profile

    def plot(self, x, y, params):
        c1 = next(self.ax._get_lines.prop_cycler)['color']
        c2 = next(self.ax._get_lines.prop_cycler)['color']
        c3 = next(self.ax._get_lines.prop_cycler)['color']

        self.data_ax.scatter(x, y, s=0.5, c=c1)

        xf = np.linspace(x.min(), x.max(), 100)
        yf = polyval(xf, params)
        self.data_ax.plot(xf, yf, color=c2)

        yfm = self.ip.get_illumination_correction(xf) * yf.max()
        self.data_ax.plot(xf, yfm, color=c3)

        # Residuals
        self.res_ax.axhline(0, ls='--', c=c2, alpha=0.3, lw=0.5)
        corrections = polyval(x, params)
        yc = y / corrections - 1
        self.res_ax.scatter(x, yc, s=0.5)

        self.data_ax.set_ylabel("Photoelectrons", labelpad=13)
        self.res_ax.set_ylabel("Residuals")
        self.res_ax.set_xlabel("Distance from Camera Centre (m)")


def process(file):
    input_path = file.dl1_path
    angular_response_path = file.angular_response_path
    illumination_profile_path = file.illumination_profile_path
    plot_dir = file.plot_dir

    ip = IlluminationProfile(angular_response_path)

    reader = DL1Reader(input_path)
    mapping = reader.mapping
    pixel, true = reader.select_columns(['pixel', 'mc_true'])
    xpix = mapping['xpix'].values
    ypix = mapping['ypix'].values
    dist = np.sqrt(xpix ** 2 + ypix ** 2)
    n_pixels = mapping.metadata['n_pixels']

    n_events = reader.n_events
    true_p = true.values.reshape((n_events, 2048)).mean(0)

    df = pd.DataFrame(dict(
        pixel=np.arange(n_pixels),
        distance=dist,
        true=true_p,
    ))

    pixel = df['pixel'].values
    true = df['true'].values
    dist = df['distance'].values

    params = polyfit(dist, true, [0, 2])
    params_norm = params/polyval(0, params)
    pixel_corrections = polyval(dist, params_norm)

    df_corr = pd.DataFrame(dict(
        pixel=pixel,
        correction=pixel_corrections,
    ))
    df_params = pd.DataFrame(params_norm)

    with HDF5Writer(illumination_profile_path) as writer:
        writer.write(correction=df_corr, params=df_params)
        writer.write_mapping(mapping)

    p_dvt = PixelScatter(ip)
    p_dvt.plot(dist, true, params)
    p_dvt.save(os.path.join(plot_dir, "illumination_profile.pdf"))

    p_f = CameraImage.from_mapping(mapping)
    p_f.image = pixel_corrections
    p_f.add_colorbar("Illumination Profile Correction")
    p_f.save(os.path.join(plot_dir, "illumination_profile_camera.pdf"))


def main():
    files = [
        d180907_MC(),
    ]
    [process(f) for f in files]


if __name__ == '__main__':
    main()
