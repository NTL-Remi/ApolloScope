import matplotlib.pyplot as plt
import numpy as np
from PIL import Image


def load(path):
    array = np.array(Image.open(path), dtype=float)

    # rescale values to metric units
    # see apolloscape.auto/scene.html#to_structure_href
    array /= 200

    return array


def colorize(array, clip=None):
    array = array.clip(0, clip)

    # rescale to [0-1]
    array /= clip or 327.68  # 327.68 = 2**16 / 200

    color_array = plt.get_cmap('turbo_r')(array)  # colorize
    color_array = color_array[:, :, :3]  # remove alpha
    color_array = np.uint8(color_array * 255)  # to [0-255]

    return Image.fromarray(color_array)
