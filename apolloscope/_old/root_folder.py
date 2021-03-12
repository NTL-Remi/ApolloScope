# -*- coding: utf-8 -*-
"""Small module for managing registration of ApolloScape root folders.

It offers a PATHS read-only mapping from dataset names to root-folders
and a setter function for each dataset path.
"""
from pathlib import Path
from types import MappingProxyType

from . import logger

__all__ = ['PATHS', 'lane_segmentation', 'scene_parsing']

_PATHS = {'scene_parsing': None,
          'lane_segmentation': None}

PATHS = MappingProxyType(_PATHS)
"""A mapping from dataset names to folder paths."""


def _make_path_setter(target):

    def path_setter(path):
        if path is None:
            return
        path = Path(path)
        if not path.exists():
            logger.error(f'Given {target} path {path} does not exist.')
            raise FileNotFoundError(f'Invalid path: "{path}"')
        _PATHS[target] = path

    return path_setter


# pylint: disable = invalid-name
scene_parsing = _make_path_setter('scene_parsing')
lane_segmentation = _make_path_setter('lane_segmentation')
