"""Functions for scanning the Scene Parsing dataset folders.

Regular expressions for the datasets' files' paths are defined
and applied to capture labels in order to sort paths in a dataframe.
"""
from pathlib import Path

import appdirs
import pandas as pd
from loguru import logger as log

from ...scene_parsing.datatype.identifier import Sequence, Type
from ...scene_parsing.path.regex import FILE_DATED

log.disable('apolloscope')


class Register:
    """Data-structure around scene parsing and lane segmentation datasets.

    Provides easy access to data by types and sequence.
    """

    CACHE_DIR = Path(appdirs.user_cache_dir('apolloscope'))
    CACHE_FILE = CACHE_DIR / 'register.csv'

    # We will organise paths in a multi-index dataframe,
    # with infos about the type of data in the columns
    # and infos about the recording run in the index dimention.
    _COLUMNS = ['section',
                'subsection',
                'file_type']

    _INDICES = ['road',
                'record',
                'camera',
                'date']

    def __init__(self, *, root, use_cache_index=False):
        if use_cache_index:
            try:
                self.dataframe = Register._df_from_cache()
                return
            except FileNotFoundError as err:
                log.warning(f'Failed loading path register from cache:\n'
                            f'{err}')

        self.dataframe = Register._df_from_file_system(root)

        self._df_to_cache()

    @staticmethod
    def _df_from_file_system(root):
        log.info('Building path register dataframe from file system')

        root = Path(root).expanduser()
        if not root.exists():
            log.error(f'Scene Parsing path not found: {root}')
            raise FileNotFoundError(f'Scene Parsing path not found: {root}')

        # extraction
        # ==========

        # get all file paths in a series as strings
        file_paths_series = pd.Series(map(str, root.glob('**/*.*')),
                                      name='path')
        log.info(f'found {file_paths_series.size} files')

        # extract index for non-pose files
        dataframe = file_paths_series.str.extract(FILE_DATED)
        # add full paths as a new column
        dataframe = pd.concat([dataframe, file_paths_series],
                              axis=1,
                              join='inner')
        # remove bad maches (non dated files)
        dataframe = dataframe.dropna()

        log.info(f'matched {len(dataframe.index)} time-stamps')

        # TODO: Pose processing to fit in the df
        # something like: dataframe['pose'] = pose_file_parsing(smth)

        # Formatting
        # ==========

        log.info('building Register')

        # convert future row index to int
        dataframe[Register._INDICES] = (dataframe[Register._INDICES]
                                        .astype('int'))
        # use columns as indices, the only left should be 'path'
        dataframe.set_index(Register._INDICES + Register._COLUMNS,
                            inplace=True)
        # move indices from row to column to fit dataframe
        dataframe = dataframe.unstack(Register._COLUMNS, fill_value=None)
        # drop the unnamed column level created by the 'path' column
        dataframe.columns = dataframe.columns.droplevel(None)

        # sorting indices, errors can arise if not done
        dataframe.sort_index(axis=1, inplace=True)
        # replacing np.nan by None
        dataframe = dataframe.where(pd.notnull(dataframe), None)

        return dataframe

    @staticmethod
    def _df_from_cache():
        log.info('Loading path register dataframe from cache')
        dataframe = pd.read_csv(
            Register.CACHE_FILE,
            header=list(range(len(Register._COLUMNS))),
            index_col=list(range(len(Register._INDICES))),
            dtype='object')

        return dataframe

    def _df_to_cache(self):
        log.info('Saving path register dataframe to cache')
        self.dataframe.to_csv(Register.CACHE_FILE)

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
