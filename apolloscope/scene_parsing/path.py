# -*- coding: utf-8 -*-
"""Functions for scanning the Scene Parsing dataset folders.

Regular expressions for the datasets' files' paths are defined
and applied to capture labels in order to sort paths in a dataframe.
"""
import os
import re
from pathlib import Path
from typing import NamedTuple, Optional

import appdirs
import pandas as pd
from loguru import logger as log

__all__ = ['Register']

log.disable('apolloscope')

CACHE_DIR = Path(appdirs.user_cache_dir('apolloscope'))


# Regular expressions
# ===================

# To sort all files in the dataset, we need to identify their content.
# In appoloscape, it is only possible through the file's name and location.
# Here we define regexes to extract relevant infos from the files' paths.
# '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

REGEX_PATH_SEP = re.escape(os.path.sep)
"""str: Regex-escaped path separator for current OS."""

REGEX_FOLDER = REGEX_PATH_SEP.join(
    [r'\w*',
     r'road(?P<road>\d+)_(?P<section>\w+?)',
     r'(?P<subsection>\w+?)',
     r'Record(?P<record>\d+)',
     r'Camera (?P<camera>\d+)'])
"""str: regex for scene parsing dataset folders."""

REGEX_FILE_DATED = re.compile(REGEX_PATH_SEP.join(
    [REGEX_FOLDER,
     r'\d+_(?P<date>\d+)_'
     r'Camera_(?P=camera)[_.]'
     r'(?P<file_type>[.\w]+?)$']))
"""re.Pattern: Compiled regex for scene parsing dataset regular files."""

REGEX_FILE_POSE = re.compile(REGEX_PATH_SEP.join(
    [REGEX_FOLDER,
     r'pose\.(?P<file_type>txt)$']))
"""re.Pattern: Compiled regex for scene parsing dataset pose files."""


# Columns and rows
# ================
# We will organise paths in a multi-index dataframe,
# with infos about the type of data in the columns
# and infos about the recording run in the index dimention.
# '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

_COLUMN_NAMES = ['section',
                 'subsection',
                 'file_type']

_INDEX_NAMES = ['road',
                'record',
                'camera',
                'date']


# class Identifier(NamedTuple):
#     @property
#     def slicer(self):
#         """Tuple[slice]: A dataframe slicer.

#         A tuple of slices that allows easy slicing of a
#         dataframe using the ``loc`` method.
#         """
#         # pylint: disable = not-an-iterable
#         return tuple(slice(_id, _id) for _id in self)
#         # note: not using pandas.IndexSlice because it is not possible
#         # to dynamically use the colon for incomplete identifiers.
#         # Thus, slice(None, None) is used instead.

#     @property
#     def is_complete(self):
#         """Bool: Define wether the identifier is completely defined."""
#         return all(map(lambda x: x is not None, self))


class Type(NamedTuple):
    """Represent a data type.

    A full data type is composed of 3  string fields :
    ``section``, ``subsection`` and ``file_type``. All fields are
    optional, enabling to define incomplete types identifiers to select
    data more broadly.

    Exemples:
        >>> Type(ins', 'Label', 'bin.png')
        Type(section='ins', subsection='Label', file_type='bin.png')
        >>> Type(subsection='ColorImage')
        Type(section=None, subsection='ColorImage', file_type=None)
    """

    section: Optional[str] = None
    """Optional[str]: The section name,
    like ``ins`` or ``seg_depth``.
    """

    subsection: Optional[str] = None
    """Optional[str]: The subsection name,
    like ``ColorImage`` or ``Depth``.
    """

    file_type: Optional[str] = None
    """Optional[str]: The file type, it is more than just the extention.
    Like ``json`` or ``bin.png``.
    """

    @property
    def slicer(self):
        """Tuple[slice]: A dataframe slicer.

        A tuple of slices that allows easy slicing of a
        dataframe using the ``loc`` method.
        """
        # pylint: disable = not-an-iterable
        return tuple(slice(_id, _id) for _id in self)
        # note: not using pandas.IndexSlice because it is not possible
        # to dynamically use the colon for incomplete identifiers.
        # Thus, slice(None, None) is used instead.

    @property
    def is_complete(self):
        """Bool: Define wether the identifier is completely defined."""
        return all(map(lambda x: x is not None, self))

    def __str__(self):  # noqa: D105
        return '{}/{}/{}'.format(*self)  # pylint: disable = not-an-iterable


class Sequence(NamedTuple):
    """Identify a sequence.

    A full sequence identifier is composed of 3  integer fields :
    ``road``, ``record`` and ``camera``. All fields are optional,
    enabling to define incomplete sequences identifiers to select data
    more broadly.

    Exemples:
        >>> Sequence(2, 1, 5)
        Sequence(road=2, record=1, camera=5)
        >>> Sequence(2, 2)
        Sequence(road=2, record=2, camera=None)
    """

    road: Optional[int] = None
    """int: The road number."""

    record: Optional[int] = None
    """int: The record number."""

    camera: Optional[int] = None
    """Optional[int]: The camera number."""

    @property
    def slicer(self):
        """Tuple[slice]: A dataframe slicer.

        A tuple of slices that allows easy slicing of a
        dataframe using the ``loc`` method.
        """
        # pylint: disable = not-an-iterable
        return tuple(slice(_id, _id) for _id in self)
        # note: not using pandas.IndexSlice because it is not possible
        # to dynamically use the colon for incomplete identifiers.
        # Thus, slice(None, None) is used instead.

    @property
    def is_complete(self):
        """Bool: Define wether the identifier is completely defined."""
        return all(map(lambda x: x is not None, self))

    def __str__(self):  # noqa: D105
        # pylint: disable = not-an-iterable
        return 'road{}/record{}/camera{}'.format(*self)  # noqa: E501


class Register:
    """Data-structure around scene parsing and lane segmentation datasets.

    Provides easy access to data by types and sequence.
    """

    def __init__(self):
        self.dataframe = None

    @staticmethod
    def from_file_system(path):
        log.info('Building path register from file system')

        path = Path(path).expanduser()
        if not path.exists():
            log.error(f'Scene Parsing path not found: {path}')
            raise FileNotFoundError(f'Scene Parsing path not found: {path}')

        register = Register.__new__(Register)

        # extraction
        # ==========

        # get all file paths in a series
        file_paths_series = pd.Series(map(str, path.glob('**/*.*')),
                                      name='path')
        log.info(f'found {file_paths_series.size} files')

        # extract index for non-pose files
        register.dataframe = file_paths_series.str.extract(REGEX_FILE_DATED)
        # add full paths as a new column
        register.dataframe = pd.concat(
            [register.dataframe, file_paths_series], axis=1, join='inner')
        # remove bad maches (non dated files)
        register.dataframe = register.dataframe.dropna()

        log.info(f'matched {len(register.dataframe.index)} time-stamps')

        # TODO: Pose processing to fit in the df
        # something like: dataframe['pose'] = pose_file_parsing(smth)

        # Formatting
        # ==========

        log.info('building Register')

        # convert future row index to int
        register.dataframe[_INDEX_NAMES] = (register.dataframe[_INDEX_NAMES]
                                            .astype('int'))
        # use columns as indices, the only left should be 'path'
        register.dataframe.set_index(
            _INDEX_NAMES + _COLUMN_NAMES, inplace=True)
        # move indices from row to column to fit dataframe
        register.dataframe = register.dataframe.unstack(
            _COLUMN_NAMES, fill_value=None)
        # drop the unnamed column level created by the 'path' column
        register.dataframe.columns = register.dataframe.columns.droplevel(None)

        # sorting indices, errors can arise if not done
        register.dataframe.sort_index(axis=1, inplace=True)
        # replacing np.nan by None
        register.dataframe = register.dataframe.where(
            pd.notnull(register.dataframe), None)

        return register

    @staticmethod
    def from_cache():
        log.info('Loading path register from cache')

        register = Register.__new__(Register)

        register.dataframe = pd.read_csv(
            CACHE_DIR / 'register.csv',
            header=list(range(len(_COLUMN_NAMES))),
            index_col=list(range(len(_INDEX_NAMES))),
            dtype='object')

        return register

    def to_cache(self):
        log.info('Saving path register to cache')
        self.dataframe.to_csv(CACHE_DIR / 'register.csv')

    def type_slice(self, type_):
        assert isinstance(type_, Type) or type_ is None
        try:
            return self.dataframe.loc[:, type_.slicer]
        except AttributeError as err:
            if type_ is None:
                return self.dataframe
            log.error(err)
            raise err

    def types(self, type_ids):
        # TODO: maybe check duplicates
        # (incomplete type usage and same types in args)
        register = Register.__new__(Register)
        register.dataframe = pd.concat((self.type_slice(type_id)
                                        for type_id in type_ids),
                                       axis=1, copy=False).dropna()
        return register

    def sequence_slice(self, sequence):
        """Return the sub-part corresponding to ``sequence``.

        Attention:
            Will return an empty dataframe if ``sequence`` does not intersect
            with the index.
        """
        assert isinstance(sequence, Sequence) or sequence is None
        try:
            return self.dataframe.loc[sequence.slicer, :]
        except AttributeError as err:  # sequence is not a Sequence
            if sequence is None:
                return self.dataframe
            log.error(err)
            raise err

    def sequences(self, sequences):
        register = Register.__new__(Register)
        register.dataframe = pd.concat([self.sequence_slice(sequence)
                                        for sequence in sequences],
                                       axis=0, copy=False).dropna()
        return register

    @property
    def type_list(self):
        raw_types = self.dataframe.columns.unique()
        return [Type(*raw_type) for raw_type in raw_types]

    @property
    def sequence_list(self):
        raw_ids = self.dataframe.index.droplevel('date').unique()
        return [Sequence(*raw_id) for raw_id in raw_ids]

    @property
    def dates(self):
        return self.dataframe.index.get_level_values('date')

    def to_series(self):
        assert len(self.dataframe.columns) == 1
        return self.dataframe.iloc[:, 0]

    def at_time(self, timestamp):
        return self.dataframe.loc[pd.IndexSlice[:, :, :, timestamp], :]
