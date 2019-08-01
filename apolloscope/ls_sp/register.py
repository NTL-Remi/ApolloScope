# -*- coding: utf-8 -*-
"""Data indexing module for ApolloScape.

This module aims to provide indexing functionalities over ApolloScape's
Scene Parsing and Lane Segmentation datasets, such as automatic
referencing and easy selection of a subpart of the dataset.

The idea is to categorise all files according to the kind of data they
contain and the recording sequence they belong to.

The undelying datastructure is a Pandas DataFrame with the type of data
on the column axis and the coresponding recording sequence on the row
axis, containing the file paths.

See Also:
    `Panda's documentation <http://pandas.pydata.org/pandas-docs/stable/>`_

Exemples:
    Build :class:`DataIndex` by scanning given paths:

    >>> INDEX = DataIndex.build(sp_path=SP_PATH,  # scene parsing path
    ...                         ls_path=LS_PATH)  # lane segmentation path

    Declare types of interest:

    >>> TYPE_A = TypeId(dataset='SP',
    ...                 section='ins',
    ...                 subsection='ColorImage',
    ...                 file_type='jpg')

    >>> TYPE_B = TypeId(dataset='SP',
    ...                 section='ins_depth',
    ...                 subsection='Depth')

    Declare sequence of interest:

    >>> SEQ_1 = SequenceId(road=2, record=1, camera=5)

    Filter subpart of interest:

    >>> INDEX = INDEX.sequences([SEQ_1]).types([TYPE_A, TYPE_B])

"""
from typing import NamedTuple, Optional

import pandas as pd

import apolloscope.root_folder
from apolloscope import logger
from . import scan

__all__ = ['TypeId', 'SequenceId', 'DataSeries', 'Register']

_COLUMN_NAMES = ['dataset',
                 'section',
                 'subsection',
                 'file_type']

_INDEX_NAMES = ['road',
                'record',
                'camera',
                'date']


class TypeId(NamedTuple):
    """Represent a data type.

    A full data type is composed of 4  string fields : ``dataset``,
    ``section``, ``subsection`` and ``file_type``. All fields are
    optional, enabling to define incomplete types identifiers to select
    data more broadly.

    Exemples:
        >>> TypeId('SP', 'ins', 'Label', 'bin.png')
        TypeId(dataset='SP', section='ins', subsection='Label', file_type='bin.png')
        >>> TypeId(subsection='ColorImage')
        TypeId(dataset=None, section=None, subsection='ColorImage', file_type=None)
    """  # noqa: E501

    dataset: Optional[str] = None
    """Optional[str]: The dataset name,
    either ``SP`` for 'Scene Parsing' or ``LS`` for 'Lane Segmentation'.
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
        """Bool: Define wether TypeId is completely defined.

        Exemples:
            >>> TypeId('SP', 'ins', 'Label', 'bin.png').is_complete
            True
            >>> TypeId(subsection='ColorImage').is_complete
            False
        """
        return all(map(lambda x: x is not None, self))

    def __str__(self):  # noqa: D105
        return '{}/{}/{}/{}'.format(*self)  # pylint: disable = not-an-iterable


class SequenceId(NamedTuple):
    """Identifies a sequence.

    A full sequence identifier is composed of 3  integer fields :
    ``road``, ``record`` and ``camera``. All fields are optional,
    enabling to define incomplete sequences identifiers to select data
    more broadly.

    Exemples:
        >>> SequenceId(2, 1, 5)
        SequenceId(road=2, record=1, camera=5)
        >>> SequenceId(2, 2)
        SequenceId(road=2, record=2, camera=None)
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

    @property
    def is_complete(self):
        """Bool: Define wether SequenceId is completely defined.

        Exemples:
            >>> SequenceId(road=2, record=1, camera=5).is_complete
            True
            >>> SequenceId(road=2, record=2).is_complete
            False
        """
        return all(map(lambda x: x is not None, self))

    def __str__(self):  # noqa: D105
        # pylint: disable = not-an-iterable
        return 'road{}/record{}/camera{}'.format(*self)  # noqa: E501


class DataSeries(pd.Series):

    @property
    def _constructor(self):
        return DataSeries

    @property
    def type_id(self):
        return TypeId(*self.name)

    @property
    def is_unique_sequence(self):
        nb_seqs = len(self.index.droplevel('date').unique())
        return nb_seqs == 1

    @property
    def sequence_id(self):
        assert self.is_unique_sequence
        raw_seq_ids = self.index.droplevel('date').unique().values
        return SequenceId(*raw_seq_ids[0])

    @property
    def dates(self):
        return self.index.get_level_values('date')

    @property
    def is_full(self):
        return self.all()


class Register(pd.DataFrame):
    """Data-structure around scene parsing and lane segmentation datasets.

    Provides easy access to data by types and sequence.
    """

    @property
    def _constructor(self):
        return Register

    @property
    def _constructor_sliced(self):
        return DataSeries

    def __init__(self, *args, **kwargs):
        if args or kwargs:
            super().__init__(*args, **kwargs)
        else:  # if first creation
            super().__init__(Register._build())

    @classmethod
    @logger.wrap_info('building  Ls-Sp Register')
    def _build(cls):
        ls_scan = None
        sp_scan = None

        ls_path = apolloscope.root_folder.PATHS['lane_segmentation']
        sp_path = apolloscope.root_folder.PATHS['scene_parsing']

        if ls_path:
            ls_scan = scan.lane_segmentation(ls_path)
        if sp_path:
            sp_scan = scan.scene_parsing(sp_path)

        if not (sp_path or ls_path):
            logger.error('both path to scene parsing '
                         'and lane segmentation are None')
            raise RuntimeError('Neither scene_parsing nor lane_segmentation '
                               'paths have been registred')
        data_index = pd.concat([ls_scan, sp_scan],
                               ignore_index=True,
                               sort=False)
        # convert future row index to int
        data_index[_INDEX_NAMES] = data_index[_INDEX_NAMES].astype('int')
        # use columns as indices, the only left should be 'path'
        data_index.set_index(_INDEX_NAMES + _COLUMN_NAMES, inplace=True)
        # move indices from row to column to fit data_index
        data_index = data_index.unstack(_COLUMN_NAMES, fill_value=None)
        # drop the unnamed column level created by the 'path' column
        data_index.columns = data_index.columns.droplevel(None)

        # sorting indices, errors can arise if not done
        data_index.sort_index(axis=1, inplace=True)
        # replacing np.nan by None
        data_index = data_index.where(pd.notnull(data_index), None)

        # TODO: merge duplicate from both datasets (colorimage for instance)
        return data_index

    def type_slice(self, type_id):
        assert isinstance(type_id, TypeId) or type_id is None
        try:
            return self.loc[:, type_id.slicer]
        except AttributeError as err:
            if type_id is None:
                return self
            logger.error(err)
            raise err

    def types(self, type_ids):
        # TODO: maybe check duplicates
        # (incomplete type usage and same types in args)
        return pd.concat((self.type_slice(type_id) for type_id in type_ids),
                         axis=1, copy=False)

    def sequence_slice(self, seq_id):
        """Return the sub-part corresponding to ``seq_id``.

        Attention:
            Will return an empty dataframe if ``seq_id`` does not intersect
            with the index.
        """
        assert isinstance(seq_id, SequenceId) or seq_id is None
        try:
            return self.loc[seq_id.slicer, :]
        except AttributeError as err:  # seq_id is not a SequenceId
            if seq_id is None:
                return self
            logger.error(err)
            raise err

    def sequences(self, seq_ids):
        return pd.concat([self.sequence_slice(seq_id) for seq_id in seq_ids],
                         axis=0, copy=False)

    @property
    def type_list(self):
        raw_types = self.columns.unique()
        return [TypeId(*raw_type) for raw_type in raw_types]

    @property
    def sequence_list(self):
        raw_ids = self.index.droplevel('date').unique()
        return [SequenceId(*raw_id) for raw_id in raw_ids]

    @property
    def dates(self):
        return self.index.get_level_values('date')

    def to_series(self):
        assert len(self.columns) == 1
        return self.iloc[:, 0]
