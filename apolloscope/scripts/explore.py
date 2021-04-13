import streamlit as st
from apolloscope import scene_parsing
from loguru import logger as log
from PIL import ImageFile
from rich.logging import RichHandler

log.enable('apolloscope')
log.configure(handlers=[{"sink": RichHandler(markup=True),
                         "format": "{message}"}])

st.set_page_config(page_title='Explore Apolloscape',
                   layout="wide")

ImageFile.LOAD_TRUNCATED_IMAGES = True


@st.cache
def get_register(use_cache_index=True):
    with st.spinner('loading register'):
        return scene_parsing.path.Register(
            root='~/Data/apolloscape/Scene_Parsing/extracted',
            use_cache_index=use_cache_index)


st_options = st.beta_expander(label='options')

use_cache_index = st_options.checkbox(label='Use disk cache for path register',
                                      value=True)


register = get_register(use_cache_index)

st_columns_selectors = st.beta_columns(2)

type_selection = st_columns_selectors[0].multiselect(
    label='type filter',
    options=register.type_list)

if type_selection:
    register = register.types(type_selection)

sequence_selection = st_columns_selectors[1].multiselect(
    label='sequence filter',
    options=register.sequence_list)

if sequence_selection:
    register = register.sequences(sequence_selection)

if len(register.dataframe) == 0:
    st.warning('types and sequences do not intersect.')
    st.stop()

time = st.select_slider(
    label="time",
    options=list(register.dates))


st_columns_downscaling = st_options.beta_columns(2)
downscale = st_columns_downscaling[0].checkbox(label='downscale images',
                                               value=True)
max_dim = None
if downscale:
    max_dim = st_columns_downscaling[1].number_input(
        label='max image length (px)',
        min_value=128,
        max_value=2048,
        value=256,
        step=128)


st_columns_depth_clip = st_options.beta_columns(2)
clip_depth = st_columns_depth_clip[0].checkbox(label='clip depth',
                                               value=True)
clip_depth_value = None
if clip_depth:
    clip_depth_value = st_columns_depth_clip[1].number_input(
        label='max depth (meters)',
        min_value=1.,
        max_value=327.68,
        value=200.,
        step=50.)


for (*sequence, timestamp), paths in register.at_time(time).iterrows():
    sequence = scene_parsing.path.Sequence(*sequence)
    paths = paths.dropna()
    st_columns = st.beta_columns(len(paths))
    for st_column, (type_, path) in zip(st_columns, paths.iteritems()):
        type_ = scene_parsing.path.Type(*type_)

        with st_column:
            try:
                image = (scene_parsing.visualization
                         .load(type_, path,
                               max_dim=max_dim,
                               depth_clip=clip_depth_value))
            except scene_parsing.visualization.DataTypeError as error:
                st.error(error)
            else:
                st.image(image, caption=f'{sequence}\t{type_}')
