# -*- coding: utf-8 -*-
from math import sqrt

import cv2

from .dataloader import DataLoader


def image_seq_player(gen, dates, title):
    for date, data in zip(dates, gen):
        try:
            data = cv2.resize(data, None, fx=0.1, fy=0.1)
            cv2.imshow(title, data)
        except cv2.error:  # data is None
            pass
        finally:
            yield title


def date_display(dates):
    for date in dates:
        print(date)
        yield


def window_tiling(w_names):
    # pylint: disable=C0103
    side = int(sqrt(len(w_names)))
    w_names = w_names.__iter__()
    y = 0
    for __ in range(side):
        x = 0
        max_h = 0
        for __, w_name in zip(range(side+1), w_names):
            cv2.moveWindow(w_name, x, y)
            __, __, w, h = cv2.getWindowImageRect(w_name)
            x += w + 50
            max_h = max(h, max_h)
        y += max_h + 50


class DataViz:

    def __init__(self, data_loader):
        self.loader = data_loader

    def play_seq(self, seq_id, types=None):
        dates, iterators = self.loader.iterators(seq_id, types)
        # remove useless nesting (single sequence)
        iterators = iterators[seq_id]
        # create image player for each iterator
        image_players = [image_seq_player(gen, dates, str(dtype))
                         for dtype, gen in iterators.items()]

        players = zip(*image_players, date_display(dates))

        # organise windows
        w_names = next(players)
        window_tiling(w_names)

        # iterate all players at once
        for __ in players:
            cv2.waitKey(1)
        cv2.destroyAllWindows()


########################################################################
########################################################################

if __name__ == '__main__':
    import pandas as pd
    import matplotlib.pyplot as plt

    from .dataindex import TypeId, SequenceId

    pd.set_option('display.max_colwidth', 10)

    DATA = DataLoader('/run/media/remi/Lacie5TB-1/'
                      'ApolloScape2/Scene_Parsing/extracted/',
                      '/run/media/remi/Lacie5TB-1/'
                      'ApolloScape2/Lane_Segmentation/extracted/')
    VIZ = DataViz(DATA)

    TYPE_1 = TypeId(dataset='SceneParsing',
                    section='ins',
                    subsection='ColorImage',
                    file_type='jpg')
    TYPE_2 = TypeId(dataset='SceneParsing',
                    section='ins_depth',
                    subsection='Depth')

    SEQ_1 = SequenceId(road=2, record=20, camera=5)

    def test_1():
        VIZ.play_seq(SEQ_1)

    # test_1()

    #######################################################

    dates, iterators = DATA.iterators(SEQ_1, TYPE_1)
    iterator = iterators[SEQ_1][TYPE_1]
    fig, ax = plt.subplots()

    def update(data):
        line.set_ydata(data)
        return line,