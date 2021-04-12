from loguru import logger as log
from PIL import Image

from . import depth, instance, semantic

log.disable('apolloscope')


def _depth_loader(path, *, clip=None):
    return depth.colorize(depth.load(path), clip=clip)


def _semantic_loader(path, *, id_type='id'):
    return semantic.colorize(semantic.remap(semantic.load(path),
                                            from_='id', to_=id_type),
                             from_=id_type)


def _instance_loader(path):
    return instance.colorize(instance.load(path))


VISUALIZATION_LOADER = {
    ('ins', 'ColorImage', 'jpg'): Image.open,
    ('seg', 'ColorImage', 'jpg'): Image.open,

    ('ins', 'Depth', 'png'): _depth_loader,
    ('ins_depth', 'Depth', 'png'): _depth_loader,
    ('seg_depth', 'Depth', 'png'): _depth_loader,

    ('ins', 'Label', 'png'): _semantic_loader,
    ('ins', 'Label', 'bin.png'): _semantic_loader,
    ('seg', 'Label', 'bin.png'): _semantic_loader,

    ('ins', 'Label', 'instanceIds.png'): _instance_loader}


class VisualizationError(Exception):
    """Base class for visualisation errors."""


class DataTypeError(VisualizationError):
    """Error related to the type of visualization."""


class LoaderError(VisualizationError):
    """Error related to image loaders."""


def load(type_, path, *, max_dim=None, depth_clip=None):
    log.debug(f'Building {type_} visualization for \'{path}\'')

    try:
        loader = VISUALIZATION_LOADER[type_]
    except KeyError as error:
        if type_ not in VISUALIZATION_LOADER.keys():
            raise DataTypeError(
                f'Unsuported type {type_}, can\'t load visualization') \
                from error
        raise

    if loader is Image.open:
        image = loader(path)
    elif loader is _depth_loader:
        image = loader(path, clip=depth_clip)
    elif loader is _semantic_loader:
        image = loader(path)
    elif loader is _instance_loader:
        image = loader(path)
    else:
        raise LoaderError(f'Unknown image loader {loader}')

    if max_dim:
        image.thumbnail((max_dim, max_dim), resample=Image.NEAREST)

    return image
