# -*- coding: utf-8 -*-
import json

import cv2
import pandas as pd

from .dataindex import DataIndex, TypeId, SequenceId


def read_img(path):
    if path:
        return cv2.imread(path, -1)
    return None


def read_json(path):
    raise NotImplementedError


def read_pose(pose_str):
    raise NotImplementedError


FORMATS = set(('json', 'png', 'bin.png', 'instanceIds.png', 'jpg'))

META_TYPE = {'png': 'image',
             'bin.png': 'image',
             'instanceIds.png': 'image',
             'jpg': 'image',
             'json': ''}

REF_2_DATA = {'json': read_json,
              'png': read_img,
              'bin.png': read_img,
              'instanceIds.png': read_img,
              'jpg': read_img}


@pd.api.extensions.register_series_accessor("load")
class _LoadSeriesAccessor:

    def __init__(self, data_series):
        assert isinstance(data_series, DataSeries)
        self.data_series = data_series

    def generator(self):
        loader = REF_2_DATA[self.data_series.type_id.file_type]
        return (loader(ref, date)
                for date, ref in zip(self.data_series.dates, self.data_series))


@pd.api.extensions.register_dataframe_accessor("load")
class _LoadDataFrameAccessor:

    def __init__(self, data_index):
        assert isinstance(data_index, DataIndex)
        self.data_index = data_index

    def sync_generators(self, seq_ids=None, data_types=None):
        raise NotImplementedError
        series_map = self.data_index.sync_series(seq_ids=seq_ids,
                                                 data_types=data_types)


def single_series(series):
    loader = REF_2_DATA[series.type_id.file_type]
    return ((date, loader(ref)) for date, ref in zip(series.dates, series))


def sync_series(data_index, seq_ids=None, types=None):
    time_series = data_index.sync_series(seq_ids, types)

    mapping = {seq_id:
               {type_id:
                # data generator over single time series
                single_series(series)
                # for each type
                for type_id, series in type_id_map.items()}
               # for each sequence
               for seq_id, type_id_map in time_series.items()}

    return mapping


class DataLoader:

    def __init__(self, sp_path=None, ls_path=None):
        self.index = DataIndex.build(sp_path=sp_path, ls_path=ls_path)

    def get_data(self, seq_id, type_id, date):
        return REF_2_DATA[type_id.file_type](self
                                             .index
                                             .get_ref(seq_id, type_id, date))

    def get_series(self, seq_id, type_id):
        series = self.index.get_series(seq_id, type_id)
        dates = series.index.get_level_values('date')
        data_gen = (REF_2_DATA[type_id.file_type](ref)
                    for ref in series.__iter__())
        return dates, data_gen

    def iterators(self, seq_ids=None, types=None):
        time_series = self.index.sync_series(seq_ids, types)

        # get a series to extract dates
        out_fst_key = list(time_series.keys())[0]
        in_fst_key = list(time_series[out_fst_key].keys())[0]
        fst_seq = time_series[out_fst_key][in_fst_key]
        # get date iterator
        dates = fst_seq.index.get_level_values('date')

        # build the nested mapping
        series_map = {seq_id:
                      {type_id:
                       # data generator over single time series
                       (REF_2_DATA[type_id.file_type](ref)
                        for ref in series.__iter__())
                       # for each type
                       for type_id, series in type_id_map.items()}
                      # for each sequence
                      for seq_id, type_id_map in time_series.items()}

        return dates, series_map


########################################################################
########################################################################

if __name__ == '__main__':
    pd.set_option('display.max_colwidth', 10)

    DATA = DataLoader(sp_path='/run/media/remi/Lacie5TB-1/ApolloScape2/'
                              'Scene_Parsing/extracted/',
                      ls_path='/run/media/remi/Lacie5TB-1/ApolloScape2/'
                              'Lane_Segmentation/extracted/')

    TYPE_1 = TypeId(dataset='SP',
                    section='ins',
                    subsection='ColorImage',
                    file_type='jpg')

    SEQ_1 = SequenceId(road=2, record=1, camera=5)

    ####################################################################

    def test_1():
        # display single type single sequence
        dates, iters = DATA.iterators([SEQ_1], [TYPE_1])
        for date, data in zip(dates, iters[SEQ_1][TYPE_1]):
            try:
                data = cv2.resize(data, None, fx=0.1, fy=0.1)
                cv2.putText(img=data,
                            text=str(date),
                            org=(0, data.shape[0] - 10),
                            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                            fontScale=0.4,
                            color=(0, 0, 255))
                cv2.imshow(str(TYPE_1), data)
                cv2.waitKey(1)
            except cv2.error:
                pass
        cv2.destroyAllWindows()

    ###################################################################
    ###################################################################

    test_1()

    ####################################################################
    ####################################################################

    # INDEX = DataIndex.build(sp_path='/run/media/remi/Lacie5TB-1/ApolloScape2/'
    #                                 'Scene_Parsing/extracted/',
    #                         ls_path='/run/media/remi/Lacie5TB-1/ApolloScape2/'
    #                                 'Lane_Segmentation/extracted/')

    # TYPE_1 = TypeId(dataset='SP',
    #                 section='ins',
    #                 subsection='ColorImage',
    #                 file_type='jpg')

    # SEQ_1 = SequenceId(road=2, record=1, camera=5)

    # def test_2():
    #     # display single type single sequence
    #     iters = sync_series(INDEX, [SEQ_1], [TYPE_1])
    #     print(iters[SEQ_1][TYPE_1])
    #     for date, data in iters[SEQ_1][TYPE_1]:
    #         print(date)
    #         try:
    #             data = cv2.resize(data, None, fx=0.1, fy=0.1)
    #             cv2.imshow(str(TYPE_1), data)
    #             cv2.waitKey(1)
    #         except cv2.error:
    #             pass
    #     cv2.destroyAllWindows()

    # test_2()
