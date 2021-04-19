"""Namespace for gloabal type shortcuts."""

from ...scene_parsing.datatype.identifier import Type

COLOR = [Type(subsection='ColorImage', file_type='jpg')]
DEPTH = [Type(subsection='Depth', file_type='png')]
INSTANCE = [Type(subsection='Label', file_type='instanceIds.png')]
SEMANTIC = [Type(subsection='Label', file_type='bin.png'),
            Type(subsection='Label', file_type='png')]
