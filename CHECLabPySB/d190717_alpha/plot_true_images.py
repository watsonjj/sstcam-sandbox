from CHECLabPy.core.io import DL1Reader
from CHECLabPy.plotting.camera import CameraImage
from CHECLabPySB import get_plot
import numpy as np


def main():
    path = "/Volumes/gct-jason/astri_onsky_archive/d2019-10-03_simulations/gamma_1deg/run1_dl1.h5"
    # path = "/Volumes/gct-jason/astri_onsky_archive/d2019-05-15_simulations/gamma_1deg/run1_dl1_old.h5"
    reader = DL1Reader(path)
    df = reader.load_entire_table()
    image = df.groupby(['pixel']).sum()['photons']

    ci = CameraImage.from_mapping(reader.mapping)
    ci.image = image
    ci.save(get_plot("d190717_alpha/true_images.pdf"))


if __name__ == '__main__':
    main()
