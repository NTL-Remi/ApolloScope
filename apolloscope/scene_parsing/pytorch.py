from functools import partial

import numpy as np
import torch
import torchvision.transforms
from einops import rearrange
from loguru import logger as log
from PIL import Image

from . import semantic
from .path import Register, Type

log.disable('apolloscope')


class Dataset(torch.utils.data.Dataset):
    _COL_BASE_TRANSFORM = torchvision.transforms.Compose([
        torchvision.transforms.Resize([128, 256], interpolation=2),
        # convert to tensor
        torchvision.transforms.ToTensor()])

    _DEP_BASE_TRANSFORM = torchvision.transforms.Compose([
        torchvision.transforms.Resize([128, 256], interpolation=2),
        # convert to tensor
        # Ideally, would be transforms.ToTensor,
        # but in current version it rescales indices TO RANGE [0,1],
        # which is not what we want.
        # Just torch.Tensor does not works either.
        # see: https://github.com/pytorch/vision/issues/1595
        partial(np.array, dtype=np.float32), torch.from_numpy,
        # get true distance
        lambda x: x / 200,
        partial(rearrange, pattern='h w -> () h w')])

    _INS_BASE_TRANSFORM = None  # TODO: implement _INS_BASE_TRANSFORM

    _SEM_BASE_TRANSFORM = torchvision.transforms.Compose([
        torchvision.transforms.Resize([128, 256], interpolation=0),
        # convert from class ids to training ids
        partial(semantic.remap, from_='id', to_='trainId'),
        # convert to tensor
        # Ideally, would be transforms.ToTensor,
        # but in current version it rescales indices to range [0,1],
        # which is not what we want.
        # Just torch.Tensor does not works either.
        # see: https://github.com/pytorch/vision/issues/1595
        partial(np.array, dtype='long'), torch.from_numpy])

    def __init__(self,
                 root=None,
                 split=None,
                 types=(),
                 transforms=None,

                 use_cache_index=True):

        types = self._format_types(types)

        if transforms:
            assert len(transforms) == len(types)
        self.transforms = transforms

        self.base_transforms = self._get_base_transforms(types)

        self.register = Register(root=root, use_cache_index=use_cache_index)
        self.register = self.register.types(types)

    def __getitem__(self, index):
        paths_series = self.register.iloc[index]
        images = [Image.open(path) for __, path in paths_series.iteritems()]
        images = self.base_transforms(*images)
        if self.transforms:
            images = self.transforms(*images)
        return images

    def __len__(self):
        return len(self.register)

    @staticmethod
    def _format_types(types):
        common_types_map = {'col': Type.COL, 'dep': Type.DEP,
                            'ins': Type.INS, 'sem': Type.SEM}
        formated_types = []
        for type_ in types:
            try:
                formated_types.extend(common_types_map[type_])
            except KeyError:
                formated_types.append(Type(type_))
        return formated_types

    @staticmethod
    def _get_base_transforms(types):
        map_ = {'color': Dataset._COL_BASE_TRANSFORM,
                'depth': Dataset._DEP_BASE_TRANSFORM,
                'instance': Dataset._INS_BASE_TRANSFORM,
                'semantic': Dataset._SEM_BASE_TRANSFORM}
        return [map_[type_.category] for type_ in types]
