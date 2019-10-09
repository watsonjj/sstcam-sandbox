from CHECLabPy.utils.mapping import get_clp_mapping_from_version
import numpy as np
from CHECLabPy.plotting.camera import CameraImage
from IPython import embed


def main():
    file = np.load("cherenkov.npz")
    cherenkov = file['frames']
    min_array = file['min']
    max_array = file['max']
    n_pixels, n_frames = cherenkov.shape

    message = np.load("happy_birthday_rich.npy")

    ci = CameraImage.from_camera_version("1.1.0")
    mapping = get_clp_mapping_from_version("1.1.0")
    rows = mapping.metadata['n_rows'] - mapping.row
    # embed()

    for iframe in range(n_frames):
        frame = cherenkov[:, iframe]
        min_ = min_array[iframe]
        max_ = max_array[iframe]
        max_row = iframe // 2

        frame_message = message.copy()
        frame_message[rows > max_row] = False
        frame[frame_message] += (max_ + min_) / 2

        ci.image = frame
        ci.set_limits_minmax(min_, max_)
        ci.save(f"frames/{iframe:03d}.png", dpi=115)


    # embed()


if __name__ == '__main__':
    main()
