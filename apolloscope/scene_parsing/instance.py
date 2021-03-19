import matplotlib.pyplot as plt
import numpy as np
from PIL import Image


def load(path):
    array = np.array(Image.open(path), dtype=np.uint8)

    return array


def colorize(array):
    remapped_array = np.empty_like(array, dtype=np.uint8)

    for i, id_ in enumerate(np.unique(array)):
        remapped_array[array == id_] = i

    color_array = plt.get_cmap('tab20')(remapped_array)  # colorize
    color_array[array == 255] = 0  # set black where empty
    color_array = color_array[:, :, :3]  # remove alpha
    color_array = np.uint8(color_array * 255)  # to [0-255]

    return Image.fromarray(color_array)
