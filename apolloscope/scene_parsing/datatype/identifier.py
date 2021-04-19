from typing import NamedTuple, Optional

__all__ = ['Type', 'Sequence']

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

    @property
    def category(self):
        # TODO: Use enum
        if self.subsection == 'ColorImage' and self.file_type == 'jpg':
            return 'color'
        if self.subsection == 'Depth' and self.file_type == 'png':
            return 'depth'
        if self.subsection == 'Label' and self.file_type == 'instanceIds.png':
            return 'instance'
        if self.subsection == 'Label' and self.file_type in ('png', 'bin.png'):
            return 'semantic'
        raise ValueError(f'Unkown type {self}.')

    @property
    def COL(self):
        return [Type(subsection='ColorImage', file_type='jpg')]

    @property
    def DEP(self):
        return [Type(subsection='Depth', file_type='png')]

    @property
    def INS(self):
        return [Type(subsection='Label', file_type='instanceIds.png')]

    @property
    def SEM(self):
        return [Type(subsection='Label', file_type='bin.png'),
                Type(subsection='Label', file_type='png')]

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
