from matplotlib import pyplot as plt
from CHECLabPy.utils.mapping import get_tm_mapping, get_clp_mapping_from_version
from CHECLabPy.plotting.camera import CameraImage
from matplotlib.patches import Rectangle, Circle
from matplotlib.collections import PatchCollection
import numpy as np
from ctapipe.image.toymodel import Gaussian, RingGaussian
from ctapipe.image.hillas import camera_to_shower_coordinates
from astropy import units as u
from IPython import embed

def print_formats(input):
    print(input, hex(input), np.binary_repr(input, width=8))

xpix = [
          -1.5, -0.5, 0.5, 1.5,
    -2.5, -1.5, -0.5, 0.5, 1.5, 2.5,
    -2.5, -1.5, -0.5, 0.5, 1.5, 2.5,
    -2.5, -1.5, -0.5, 0.5, 1.5, 2.5,
    -2.5, -1.5, -0.5, 0.5, 1.5, 2.5,
          -1.5, -0.5, 0.5, 1.5,
]
ypix = [
           2.5,  2.5,  2.5,  2.5,
     1.5,  1.5,  1.5,  1.5,  1.5,  1.5,
     0.5,  0.5,  0.5,  0.5,  0.5,  0.5,
    -0.5, -0.5, -0.5, -0.5, -0.5, -0.5,
    -1.5, -1.5, -1.5, -1.5, -1.5, -1.5,
          -2.5, -2.5, -2.5, -2.5,
]
size = 0.9
n_pixels = 32

patches = []
for xx, yy in zip(xpix, ypix):
    rr = size
    poly = Rectangle(
        (xx - rr / 2., yy - rr / 2.),
        width=rr,
        height=rr,
        fill=True,
    )
    patches.append(poly)

fig, ax = plt.subplots()

pixels = PatchCollection(patches, linewidth=0)
ax.add_collection(pixels)
pixels.set_array(np.zeros(n_pixels))

ax.set_aspect('equal', 'datalim')
ax.set_xlabel("X position (m)")
ax.set_ylabel("Y position (m)")
ax.autoscale_view()
ax.axis('off')

colorbar = ax.figure.colorbar(
    pixels, pad=-0.2, ax=ax
)

xpix = np.array(xpix) * u.m
ypix = np.array(ypix) * u.m

def convert(a, t):
    return f"0x{hex(a << 4 | (t & 0xF))[2:].zfill(2)}"

z_next = False

for i in range(100):
    rand = np.random.RandomState(i)

    x = rand.uniform(-1, 1, 1)[0] * u.m
    y = rand.uniform(-1, 1, 1)[0] * u.m
    length = rand.uniform(1, 2.5, 1)[0] * u.m
    width = rand.uniform(0.5, 0.9, 1)[0] * u.m
    psi = rand.uniform(0, 360, 1)[0] * u.deg
    radius = 2.2 * u.m
    sigma = 0.3 * u.m
    max_time = rand.uniform(4, 7, 1)[0]
    max_amp = 15#rand.uniform(10, 15, 1)[0]

    longi, trans = camera_to_shower_coordinates(xpix, ypix, x, y, psi)
    time = longi - longi.min()
    time = np.round(time * max_time / time.max()).value.astype(np.int)

    type_rand = np.round(rand.uniform(1, 20, 1)[0])
    if z_next:
        image = np.zeros(32, dtype=np.int)
        image[[5, 6, 7, 8, 13, 18, 25, 24, 23, 26]] = 5
        z_next = False
    elif type_rand == 3:
        image = np.zeros(32, dtype=np.int)
        image[[5, 6, 7, 8, 13, 19, 25, 24, 23]] = 5
        z_next = True
    elif type_rand == 7:
        ring = RingGaussian(x, y, radius, sigma)
        image = ring.pdf(xpix, ypix)
        image = np.round(image * max_amp / image.max()).astype(np.int)
        time = np.full(32, 5, dtype=np.int)
    else:
        gaussian = Gaussian(x, y, length, width, psi)
        image = gaussian.pdf(xpix, ypix)
        image = np.round(image * max_amp / image.max()).astype(np.int)

    array = [convert(a, t) for a, t in zip(image, time)]

    print(
        f"    {{{array[0]},{array[1]},{array[2]},{array[3]},\n"
        f"{array[4]},{array[5]},{array[6]},{array[7]},{array[8]},{array[9]},\n"
        f"{array[10]},{array[11]},{array[12]},{array[13]},{array[14]},{array[15]},\n"
        f"{array[16]},{array[17]},{array[18]},{array[19]},{array[20]},{array[21]},\n"
        f"{array[22]},{array[23]},{array[24]},{array[25]},{array[26]},{array[27]},\n"
        f"     {array[28]},{array[29]},{array[30]},{array[31]}}},"
    )

    # pixels.set_array(np.ma.masked_invalid(image))
    # pixels.changed()
    # ax.figure.canvas.draw()
    #
    # pixels.autoscale()
    # plt.pause(1)