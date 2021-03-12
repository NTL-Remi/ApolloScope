import numpy as np
import streamlit
from apolloscope import scene_parsing
from loguru import logger as log
from PIL import Image, ImageFile, ImageMath
from rich.logging import RichHandler

log.enable('apolloscope')
log.configure(handlers=[{"sink": RichHandler(markup=True),
                         "format": "{message}"}])

streamlit.set_page_config(layout="wide")
ImageFile.LOAD_TRUNCATED_IMAGES = True


@streamlit.cache
def get_register(use_disk_cache=True):
    with streamlit.spinner('loading register'):
        if use_disk_cache:
            try:
                register = scene_parsing.path.Register.from_cache()
                return register
            except FileNotFoundError:
                pass

        register = scene_parsing.path.Register.from_file_system(
            '~/Data/apolloscape/Scene_Parsing/extracted')

        if use_disk_cache:
            register.to_cache()

    return register


def load_visualization_from_path(type_, path):
    if type_ == ('ins', 'Label', 'json'):
        # TODO: Implement json visualization
        streamlit.warning(f'visualisation not implemented for {type_}')
    else:
        image = Image.open(path)
        try:
            image = (scene_parsing.visualization
                     .VISUALIZE_TYPE_FUCTION[type_](image))
        except AttributeError:
            streamlit.error(f"Can't visualize type {type_}")
    return image


use_disk_cache = streamlit.checkbox(label="Use disk cache for path register",
                                    value=True)

register = get_register(use_disk_cache)

streamlit_columns_selectors = streamlit.beta_columns(2)

type_selector = streamlit_columns_selectors[0].empty()
type_selection = type_selector.multiselect(
    label='type filter',
    options=register.type_list)

sequence_selector = streamlit_columns_selectors[1].empty()
sequence_selection = sequence_selector.multiselect(
    label='sequence filter',
    options=register.sequence_list)

if type_selection:
    register = register.types(type_selection)

if len(register.dataframe) == 0:
    streamlit.warning("types and sequences do not intersect.")
else:
    time = streamlit.select_slider(
        label="time",
        options=list(register.dates))

    for (*sequence, timestamp), paths in register.at_time(time).iterrows():
        sequence = scene_parsing.path.Sequence(*sequence)
        paths = paths.dropna()
        st_columns = streamlit.beta_columns(len(paths))
        for st_column, (type_, path) in zip(st_columns, paths.iteritems()):
            type_ = scene_parsing.path.Type(*type_)

            with st_column:
                try:
                    image = (scene_parsing.visualization
                             .get_from_path(type_, path, ratio=0.1))
                except scene_parsing.visualization.DataTypeError as error:
                    streamlit.error(error)
                else:
                    streamlit.image(image, caption=f'{sequence}\t{type_}')
