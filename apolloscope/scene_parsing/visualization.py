import numpy as np
from loguru import logger as log
from PIL import Image

from . import depth, instance, semantic

log.disable('apolloscope')


def _visualization_loader(type_module):
    return lambda path: type_module.colorize(type_module.load(path))


VISUALIZATION_LOADER = {
    ('ins', 'ColorImage', 'jpg'): Image.open,
    ('seg', 'ColorImage', 'jpg'): Image.open,

    ('ins', 'Depth', 'png'): _visualization_loader(depth),
    ('ins_depth', 'Depth', 'png'): _visualization_loader(depth),
    ('seg_depth', 'Depth', 'png'): _visualization_loader(depth),

    ('ins', 'Label', 'png'): _visualization_loader(semantic),
    ('ins', 'Label', 'bin.png'): _visualization_loader(semantic),
    ('seg', 'Label', 'bin.png'): _visualization_loader(semantic),

    ('ins', 'Label', 'instanceIds.png'): _visualization_loader(instance)}

# COLORIZE_TYPE_FUCTION = {
#     ('ins', 'ColorImage', 'jpg'): lambda array: array,
#     ('seg', 'ColorImage', 'jpg'): lambda array: array,

#     ('ins', 'Depth', 'png'): depth.colorize,
#     ('ins_depth', 'Depth', 'png'): depth.colorize,
#     ('seg_depth', 'Depth', 'png'): depth.colorize,

#     ('ins', 'Label', 'png'): semantic.colorize,
#     ('ins', 'Label', 'bin.png'): semantic.colorize,
#     ('seg', 'Label', 'bin.png'): semantic.colorize,

#     ('ins', 'Label', 'instanceIds.png'): instance.colorize}


class VisualizationError(Exception):
    """Base class for visualisation errors."""


class DataTypeError(VisualizationError):
    """Error related to the type of visualization."""


def get_from_path(type_, path, *, resize=None, ratio=None):
    log.debug(f'Building {type_} visualization for \'{path}\'')
    try:
        image = VISUALIZATION_LOADER[type_]
    except KeyError as error:
        raise DataTypeError(
            f'Unsuported type {type_}, can not load visualization') \
            from error

    if ratio is not None:
        resize = (int(image.size[0] * ratio),
                  int(image.size[1] * ratio))
    if resize is not None:
        image = image.resize(resize)

    return image

# def get_from_path(type_, path, *, resize=None, ratio=None):
#     log.debug(f'Building {type_} visualization for \'{path}\'')
#     try:
#         colorization_function = COLORIZE_TYPE_FUCTION[type_]
#     except KeyError as error:
#         raise DataTypeError(
#             f'Unsuported type {type_}, can not load visualization') \
#             from error

#     image = Image.open(path)
#     image = colorization_function(image)

#     if ratio is not None:
#         resize = (int(image.size[0] * ratio),
#                   int(image.size[1] * ratio))
#     if resize is not None:
#         image = image.resize(resize)

#     return image
