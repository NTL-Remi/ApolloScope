# -*- coding: utf-8 -*-
from contextlib import contextmanager

import matplotlib.pyplot as plt
import missingno

import apolloscope

apolloscope.logger.LoggingSetUp().default()

apolloscope.root_folder.scene_parsing(
    '/media/ip_ispr/Lacie5TB-1/ApolloScape2/Scene_Parsing/extracted')
apolloscope.root_folder.lane_segmentation(
    '/media/ip_ispr/Lacie5TB-1/ApolloScape2/Lane_Segmentation/extracted')

REGISTER = apolloscope.ls_sp.register.Register()

SEQ_1 = apolloscope.ls_sp.register.SequenceId(road=2, record=22, camera=5)
SEQ_2 = apolloscope.ls_sp.register.SequenceId(road=2, record=1)

TYPE_1 = apolloscope.ls_sp.register.TypeId('SP', 'seg', 'ColorImage', 'jpg')
TYPE_2 = apolloscope.ls_sp.register.TypeId('SP', 'seg_depth', 'Depth', 'png')

SELECTION = REGISTER.sequences([SEQ_1, SEQ_2]).types([TYPE_1, TYPE_2])

# fig_1 = missingno.matrix(REGISTER)
# fig_2 = missingno.heatmap(REGISTER)
# fig_3 = missingno.dendrogram(REGISTER)
# plt.show()

dataset = apolloscope.ls_sp.pytorch.Dataset(SELECTION)
dataset[0][0].show()

########################################################################

# apolloscope.set_ls_root_folder('gné')
# apolloscope.set_sp_root_folder('gné')
# dataloader = apolloscope.ls_sp.Dataloader()