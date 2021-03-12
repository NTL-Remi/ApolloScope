import matplotlib.pyplot as plt
import numpy as np
from einops import repeat
from loguru import logger as log
from PIL import Image

from . import semantic

log.disable('apolloscope')


def colorize_depth(array, clip=200):
    # rescale values to metric units
    # see apolloscape.auto/scene.html#to_structure_href
    array = np.array(array, dtype=float) / 200
    array = array.clip(0, clip)  # clip at 200 meters
    array /= clip  # rescale to [0-1]

    color_array = plt.get_cmap('turbo_r')(array)  # colorize
    color_array = color_array[:, :, :3]  # remove alpha
    color_array = np.uint8(color_array * 255)  # to [0-255]

    return Image.fromarray(color_array)


def colorize_semantic(array):
    array = np.array(array, dtype=np.uint8)
    # create 3-channel output array
    color_array = repeat(np.empty_like(array),
                         'h w -> h w c', c=3)

    # fill color by color
    color_map = semantic.mapping('id', to='color')
    for id_ in np.unique(array):
        color_array[array == id_] = np.uint8(color_map[id_])

    return Image.fromarray(color_array)


def colorize_instances(array):
    array = np.array(array, dtype=np.uint8)

    remapped_array = np.empty_like(array)
    for i, id_ in enumerate(np.unique(array)):
        remapped_array[array == id_] = i

    color_array = plt.get_cmap('tab20')(remapped_array)  # colorize
    color_array[array == 255] = 0  # set black where empty
    color_array = color_array[:, :, :3]  # remove alpha
    color_array = np.uint8(color_array * 255)  # to [0-255]

    return Image.fromarray(color_array)


COLORIZE_TYPE_FUCTION = {
    ('ins', 'ColorImage', 'jpg'): lambda array: array,
    ('seg', 'ColorImage', 'jpg'): lambda array: array,

    ('ins', 'Depth', 'png'): colorize_depth,
    ('ins_depth', 'Depth', 'png'): colorize_depth,
    ('seg_depth', 'Depth', 'png'): colorize_depth,

    ('ins', 'Label', 'png'): colorize_semantic,
    ('ins', 'Label', 'bin.png'): colorize_semantic,
    ('seg', 'Label', 'bin.png'): colorize_semantic,

    ('ins', 'Label', 'instanceIds.png'): colorize_instances}


class VisualizationError(Exception):
    """Base class for visualisation errors."""


class DataTypeError(VisualizationError):
    """Error related to the type of visualization."""


def get_from_path(type_, path, *, resize=None, ratio=None):
    log.debug(f'Building {type_} visualization for {path}')
    try:
        colorization_function = COLORIZE_TYPE_FUCTION[type_]
    except KeyError as error:
        raise DataTypeError(
            f'Unsuported type {type_}, can not load visualization') \
            from error

    image = Image.open(path)
    image = colorization_function(image)

    if ratio is not None:
        resize = (int(image.size[0] * ratio),
                  int(image.size[1] * ratio))
    if resize is not None:
        image = image.resize(resize)

    return image


def get_from_array(type_, array, *, resize=None, ratio=None):
    log.debug(f'Building {type_} visualization for {array}')
    try:
        colorization_function = COLORIZE_TYPE_FUCTION[type_]
    except KeyError as error:
        raise DataTypeError(
            f'Unsuported type {type_}, can not load visualization') \
            from error

    image = colorization_function(array)

    if ratio is not None:
        resize = (int(image.size[0] * ratio),
                  int(image.size[1] * ratio))
    if resize is not None:
        image = image.resize(resize)

    return image
