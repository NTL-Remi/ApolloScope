"""Helper script to manage Cityscapes labels.

This script is based on
`cityscapesScripts <https://github.com/mcordts/cityscapesScripts>`_'s
``/helpers/labels.py`` file,
it is used to create dictionaries for a fast lookup of label informations
(see  :func:`mapping`). It also defines utility functions for arrays:
mapping from one kind of id to another (:func:`map_ids`),
and colorizing according to ids (:func:`colorize`).

The following table presents label informations fields:

==================  ===========================================================
Fields              Descriptions
==================  ===========================================================
``name``            The identifier of this label,
                    *e.g.* ``car``, ``person``, ... .
                    We use them to uniquely name a class.
------------------  -----------------------------------------------------------
``id``              An integer ID that is associated with this label.
                    The IDs are used to represent the label
                    in ground truth images.
                    An ID of -1 means that this label does not have an ID
                    and thus is ignored when creating ground truth images
                    (*e.g.* license plate).
                    Do not modify these IDs, since exactly these IDs
                    are expected by the evaluation server.
------------------  -----------------------------------------------------------
``trainId``         Feel free to modify these IDs
                    as suitable for your method.
                    Then create ground truth images with train IDs,
                    using the tools provided in the 'preparation' folder.
                    However, make sure to validate or submit results
                    to our evaluation server using the regular IDs above!
                    For trainIds, multiple labels might have the same ID.
                    Then, these labels are mapped to the same class
                    in the ground truth images.
                    For the inverse mapping,
                    we use the label that is defined first in the list below.
                    For example, mapping all void-type classes to the same ID
                    in training, might make sense for some approaches.
                    Max value is 255!
------------------  -----------------------------------------------------------
``category``        The name of the category that this label belongs to.
------------------  -----------------------------------------------------------
``catId``           The ID of this category.
                    Used to create ground truth images on category level.
------------------  -----------------------------------------------------------
``hasInstances``    Whether this label distinguishes
                    between single instances or not.
------------------  -----------------------------------------------------------
``ignoreInEval``    Whether pixels having this class as ground truth label
                    are ignored during evaluations or not.
------------------  -----------------------------------------------------------
``color``           The color of this label.
------------------  -----------------------------------------------------------
``description``     The description of this label as found on the
                    `Cityscapes website
                    <https://www.cityscapes-dataset.com/dataset-overview/
                    #class-definitions>`_
==================  ===========================================================

.. Note::
  cityscapesScripts put the following in their `label script`_ comments
  just before defining each label:

    Please adapt the train IDs as appropriate for you approach in `labels.csv`.
    Note that you might want to ignore labels with ID 255 during training.
    Further note that the current train IDs are only a suggestion.
    You can use whatever you like.
    Make sure to provide your results using the original IDs
    and not the training IDs.
    Note that many IDs are ignored in evaluation
    and thus you never need to predict these!

  In our case we moved the label definitions to a CSV file
  to be read with Pandas.
  In `labels.csv` label declaration are in reverse order of what is done in
  cityscapesScripts' labels.py to keep the same mapping
  from `trainId` to `id`: while `cityscapesScripts` prioritize the first label
  with matching `trainId`, `Pandas`' `Series`' `to_dict` method prioritizes
  the last.

.. _label script: https://github.com/mcordts/cityscapesScripts/
                  blob/master/cityscapesscripts/helpers/labels.py
                  #L56
"""

from pathlib import Path

import pandas as pd
from PIL.ImageColor import getrgb

LABEL_TABLE = pd.read_csv(
    Path(__file__).parent / 'semantic.csv',
    dtype={
        # Use of `'string'` instead of `str` dtype
        # so that Pandas uses its string type
        # instead of a generic object type.
        'name': 'string',
        # /!\ if using np.uint8 for id dtypes,
        # ids of -1 (like `license plate`)
        # will be warped to 255.
        'id': int,
        'trainId': int,
        'category': 'string',
        'catId': int,
        'hasInstances': bool,
        'ignoreInEval': bool,
        'description': 'string'},
    converters={
        # color is given as a hexcode to be storable
        # in a csv file, so it needs additional processing
        'color': getrgb})


def mapping(from_: str, to: str):
    """Create dictionaries for a fast lookup.

    Examples:
        >>> mapping('name', to='id')['car']
        33
        >>> mapping('id', to='category')[33]
        'vehicle'
        >>> mapping('trainId', to='name')[0]
        'road'
    """
    return LABEL_TABLE.set_index(from_)[to].to_dict()
