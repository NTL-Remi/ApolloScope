# -*- coding: utf-8 -*-
from typing import NamedTuple


class PoseData(NamedTuple):
    """Container object for data described in pose files."""

    r00: float
    r01: float
    r02: float

    r10: float
    r11: float
    r12: float

    r20: float
    r21: float
    r22: float

    t0: float
    t1: float
    t2: float


def pose_file_parsing(file_path):
    raise NotImplementedError
