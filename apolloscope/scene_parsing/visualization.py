from functools import partial

from loguru import logger as log
from PIL import Image

from . import depth, instance, semantic
from .path import Type

log.disable('apolloscope')


def _color_loader(path):
    return Image.open(path)


def _depth_loader(path, *, clip=None):
    return depth.colorize(depth.load(path), clip=clip)


def _instance_loader(path):
    return instance.colorize(instance.load(path))


def _semantic_loader(path, *, id_type='id'):
    return semantic.colorize(semantic.remap(semantic.load(path),
                                            from_='id', to_=id_type),
                             from_=id_type)


def load(type_, path, *, max_dim=None, depth_clip=None):
    log.debug(f'Building {type_} visualization for \'{path}\'')

    type_ = Type(*type_)

    loader_map = {'color': _color_loader,
                  'depth': partial(_depth_loader, clip=depth_clip),
                  'instance': _instance_loader,
                  'semantic': _semantic_loader}

    image = loader_map[type_.category](path)

    if max_dim:
        image.thumbnail((max_dim, max_dim), resample=Image.NEAREST)

    return image
