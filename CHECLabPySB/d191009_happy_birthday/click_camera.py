from CHECLabPy.plotting.camera import CameraImage
import numpy as np
from matplotlib import pyplot as plt


class CameraImageClick(CameraImage):
    def __init__(self, xpix, ypix, size, **kwargs):
        super().__init__(xpix, ypix, size, **kwargs)
        self.click_radius = size
        self.image = np.zeros(xpix.size, dtype=np.bool)

        self.pixels.set_picker(True)  # enable click
        self.pixels.set_pickradius(self.click_radius)
        self.pixels.set_snap(True)  # snap cursor to pixel center
        self.fig.canvas.mpl_connect('pick_event', self._on_pick)

    def _on_pick(self, event):
        pix_id = event.ind[-1]
        print(f"Clicked pixel: {pix_id}")
        image = self.image.copy()
        image[pix_id] = ~image[pix_id]
        self.image = image


ci = CameraImageClick.from_camera_version("1.1.0")
plt.show()
np.save("click_camera.npy", ci.image)
