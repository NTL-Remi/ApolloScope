import cv2
import numpy as np
import torch
import torch.utils.data


class Dataset(torch.utils.data.dataset.Dataset):
    def __init__(self, register):
        self.register = register.dropna()

    def __getitem__(self, index):
        paths_series = self.register.iloc[index]
        images = [load_image(path, index)
                  for index, path in paths_series.iteritems()]
        return images

    def __len__(self):
        return len(self.register)


def load_image(path, index, resize=None):
    img = cv2.imread(path, -1)
    if resize:
        img = cv2.resize(img, resize, interpolation=cv2.INTER_AREA)

    if index[2] == 'ColorImage':
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = np.transpose(img, (2, 0, 1))  # pytorch format
        img = img.astype(np.float32) / 255

    elif index[1] == 'seg' and index[2] == 'Label':
        img = np.stack([img == index for index in range(36)], axis=0)
        img = img.astype(np.float32)

    elif index[2] == 'Depth':
        img = img.astype(np.float32) / 65535.0  # normalise
        img = np.expand_dims(img, axis=0)  # add channel dim
    else:
        raise NotImplementedError(
            f'loading not implemented for image of type {index}'
        )
    return img


if __name__ == '__main__':
    import apolloscope
    from apolloscope.ls_sp.register import Register, SequenceId, TypeId
    from matplotlib import pyplot as plt
    from pathlib import Path

    sp_path = (Path.home() / 'Data' / 'apolloscape' /
               'Scene_Parsing' / 'extracted')
    # ls_path = (Path.home() / 'Data' / 'apolloscape' /
    #            'Lane_Segmentation' / 'extracted')

    apolloscope.root_folder.scene_parsing(sp_path.resolve(strict=True))
    # apolloscope.root_folder.lane_segmentation(ls_path.resolve(strict=True))

    _INDEX = Register()

    _IMAGE_TYPE = TypeId("SP", "seg", "ColorImage", "jpg")
    _DEPTH_TYPE = TypeId("SP", "seg_depth", "Depth", "png")

    _TEST_SEQUENCE = SequenceId(2, 22, 6)

    _REGISTER = _INDEX.sequences([_TEST_SEQUENCE])
    _REGISTER = _REGISTER.types([_IMAGE_TYPE, _DEPTH_TYPE])

    _DATASET = Dataset(_REGISTER)

    for (im, dep) in _DATASET:
        plt.imshow(im.transpose((1, 2, 0)))
        plt.show()

        plt.imshow(dep.transpose((1, 2, 0)).squeeze())
        plt.show()
