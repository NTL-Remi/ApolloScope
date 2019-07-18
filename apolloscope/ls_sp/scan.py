# -*- coding: utf-8 -*-
import os
import re
from pathlib import Path

import pandas as pd

from apolloscope import logger

__all__ = ['scene_parsing', 'lane_segmentation']

REGEX_PATH_SEPARATOR = re.escape(os.path.sep)
"""str: Regex-escaped path separator for current OS."""

SP_FOLDER_REGEX = REGEX_PATH_SEPARATOR.join(
    [r'.*',
     r'road(?P<road>[0-9]+)_(?P<section>.*?)',
     r'(?P<subsection>.*?)',
     r'Record(?P<record>[0-9]+)',
     r'Camera (?P<camera>[0-9]+)'])
"""str: Compiled regex for scene parsing dataset folders."""

SP_DATED_FILE_REGEX = re.compile(REGEX_PATH_SEPARATOR.join(
    [SP_FOLDER_REGEX,
     r'[0-9]+_(?P<date>[0-9]+)_'
     r'Camera_[0-9][_.]'
     r'(?P<file_type>.*?)$']))
"""re.Pattern: Compiled regex for scene parsing dataset regular files."""

SP_POSE_FILE_REGEX = re.compile(REGEX_PATH_SEPARATOR.join(
    [SP_FOLDER_REGEX,
     r'pose\.(?P<file_type>txt)$']))
"""re.Pattern: Compiled regex for scene parsing dataset pose files."""

LS_FOLDER_REGEX = REGEX_PATH_SEPARATOR.join(
    [r'.*',
     r'(?P<section>.*?)_road(?P<road>[0-9]+)',
     r'(?P<subsection>.*?)',
     r'Record(?P<record>[0-9]+)',
     r'Camera (?P<camera>[0-9]+)'])
"""str: Compiled regex for lane segmentation dataset folders."""

LS_FILE_REGEX = re.compile(REGEX_PATH_SEPARATOR.join(
    [LS_FOLDER_REGEX,
     r'[0-9]+_(?P<date>[0-9]+)_'
     r'Camera_[0-9][_.]'
     r'(?P<file_type>.*?)$']))
"""re.Pattern: Compiled regex for lane segmentation dataset files."""


@logger.wrap_info('scanning Scene_Parsing')
def scene_parsing(path):
    """Look for 'Scene Parsing' dataset's files and categorise them.

    Args:
        path (Path): Root folder of 'Scene Parsing' dataset

    Return:
        pd.DataFrame: A dataframe with columns ``dataset``, ``section``,
            ``subsection``, ``file_type``, ``road``, ``record``,
            ``camera``, ``date`` and ``path``.
            ``path`` contains all the file paths found in the
            ``path`` directory, and other columns contain labels
            extracted from them.
    """
    # TODO: move the path checking to a higher level
    # assert path is valid
    if path is None:
        return None
    path = Path(path)
    if not path.exists():
        logger.error(f'Scene Parsing path not found: "{path}"')
        return None

    # get all file paths in a series
    file_paths_series = pd.Series(map(str, path.glob('**/*.*')), name='path')
    logger.info(f'found {file_paths_series.size} files')

    # extract index for non-pose files
    dataframe = file_paths_series.str.extract(SP_DATED_FILE_REGEX).dropna()
    # reintroduce full paths as a new column
    dataframe = pd.concat([dataframe, file_paths_series], axis=1, join='inner')

    logger.info(f'matched {len(dataframe.index)} time-stamped data files')

    dataframe['dataset'] = 'SP'

    # TODO: Pose processing to fit in the df
    # something like: dataframe['pose'] = pose_file_parsing(smth)

    return dataframe


@logger.wrap_info('scanning Lane_Segmentation')
def lane_segmentation(path):
    """Look for 'Lane Segmentation' dataset's files.

    Args:
        path (Path): Root folder of 'Lane Segmentation' dataset
    """
    # assert path is valid
    if path is None:
        return None
    path = Path(path)
    if not path.exists():
        logger.error(f'lane segmentation path not found: "{path}"')
        return None

    # get all file paths in a series
    file_paths_series = pd.Series(map(str, path.glob('**/*.*')), name='path')
    logger.info(f'found {file_paths_series.size} files')
    dataframe = file_paths_series.str.extract(LS_FILE_REGEX)
    # reintroduce full paths as a new column
    dataframe = pd.concat([dataframe, file_paths_series], axis=1, join='inner')
    logger.info(f'matched {len(dataframe.index)} time-stamped data files')

    dataframe['dataset'] = 'LS'

    return dataframe
