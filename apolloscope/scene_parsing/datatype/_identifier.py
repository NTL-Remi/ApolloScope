from __future__ import annotations

import operator
from copy import deepcopy
from functools import cached_property, reduce
from typing import Hashable, List, Mapping, Optional, Set


class Identifier:
    """Apolloscape identifier representation.

    A fully defined identifier is composed of 3 hierarchical fields
    ``Rank_1``, ``Rank_2`` and ``Rank_3``.

    All fields are optional,
    enabling to define incomplete identifiers
    to select data more broadly.

    Exemples:
        >>> Identifier(1, 2, 3)
        Identifier(1, 2, 3)
        >>> Identifier(rank_2=2)
        Identifier(None, 2, None)

    Using incomplete ids will catch every values for unspecified fields.
    To get a finer control over which data is selected,
    identifiers can be composed.
    Composing such 'fundamental ids' results in a 'composite ids'.

    Examples:
        >>> (Identifier('ins', 'Label', 'bin.png')
        ...  + Identifier('ins', 'Depth', 'png'))
        Identifier(ins, Depth, png) | Identifier(ins, Label, bin.png)
    """

    Rank_1 = Optional[Hashable]
    Rank_2 = Optional[Hashable]
    Rank_3 = Optional[Hashable]

    Rank3Set = Set[Rank_3]
    Rank2Map = Mapping[Rank_2, Rank3Set]
    Rank1Map = Mapping[Rank_1, Rank2Map]

    def __init__(self,
                 rank_1: Rank_1 = None,
                 rank_2: Rank_2 = None,
                 rank_3: Rank_3 = None):

        self._rank_1_map: Identifier.Rank1Map = {rank_1:
                                                 {rank_2:
                                                  {rank_3}}}

    @cached_property
    def components(self) -> Set[Identifier]:
        """Return the set of composing fundamental ids.

        Exemples:
            TODO
        """
        return set(self._sorted_components)

    @cached_property
    def is_composite(self) -> bool:
        """Is True if the identifier has multiple fundamental component ids.

        Examples:
            >>> simple_id = Identifier(1, 2, 3)
            >>> simple_id.is_composite
            False
            >>> composite_id = Identifier(1, 2, 3) | Identifier(11, 12, 13)
            >>> composite_id.is_composite
            True
        """
        return len(self.components) > 1

    @cached_property
    def is_definite(self) -> bool:
        """Is True if the identifier does not have catch-all fields.

        Examples:
            >>> definite_id = Identifier(1, 2, 3)
            >>> definite_id.is_definite
            True
            >>> undefinite_id = Identifier(1, None, 3)
            >>> undefinite_id.is_definite
            False
        """
        try:
            return (self._rank_1 is not None
                    and self._rank_2 is not None
                    and self._rank_3 is not None)
        except self.CompositeError:
            return all(component.is_definite for component in self.components)

    @property
    def _rank_1(self) -> Rank_1:
        """Return the Identifier rank_1 if it is not composite.

        Raise:
            Identifier.CompositeError: The Identifier has more than one rank_1.

        Exemples:
            >>> simple_id = Identifier(1, 2, 3)
            >>> simple_id._rank_1
            1
            >>> composite_id = Identifier(1, 2, 3) | Identifier(11, 12, 13)
            >>> composite_id._rank_1
            Traceback (most recent call last):
            CompositeError: Identifier._rank_1 is undefined
        """
        try:
            if len(self._rank_1_map) > 1:
                raise self.CompositeError(
                    'Identifier has multiple rank 1 values')
        except self.CompositeError as err:
            raise self.CompositeError(
                'Identifier.rank_1 is undefined') from err
        return list(self._rank_1_map.keys())[0]

    @property
    def _rank_2(self) -> Rank_2:
        """Return the Identifier rank_2 if it is not composite.

        Raise:
            Identifier.CompositeError: The Identifier has more than one rank_1
                or more than one rank_2.

        Exemples:
            TODO
        """
        try:
            subsection_tree = self._rank_1_map[self._rank_1]
            if len(subsection_tree) > 1:
                raise self.CompositeError(
                    'Identifier has multiple rank 2 values')
        except self.CompositeError as err:
            raise self.CompositeError(
                'Identifier.rank_2 is undefined') from err
        return list(subsection_tree.keys())[0]

    @property
    def _rank_3(self) -> Rank_3:
        """Return the Identifier file format if it is not composite.

        Raise:
            Identifier.CompositeError: The Identifier has more than one rank_1
                or more than one rank_2
                or more than one file format.

        Exemples:
            TODO
        """
        try:
            rank_3_set = self._rank_1_map[self._rank_1][self._rank_2]
            if len(rank_3_set) > 1:
                raise self.CompositeError(
                    'Identifier has multiple rank 3 values')
        except self.CompositeError as err:
            raise self.CompositeError(
                'Identifier.rank_3 is undefined') from err
        return list(rank_3_set)[0]

    @property
    def tuple(self):
        try:
            return (self._rank_1, self._rank_2, self._rank_3)
        except self.CompositeError as err:
            raise self.CompositeError('Not representable as a tuple') from err

    def __or__(self, other: Identifier) -> Identifier:
        return type(self)._from_components(self, other)

    def __add__(self, other: Identifier) -> Identifier:
        return self | other

    def __eq__(self, other: Identifier) -> bool:  # noqa: D105
        return self._rank_1_map == other._rank_1_map

    def __le__(self, other: Identifier) -> bool:
        return self.components <= other.components

    def __ge__(self, other: Identifier) -> bool:
        return self.components >= other.components

    def __lt__(self, other: Identifier) -> bool:
        return self.components < other.components

    def __gt__(self, other: Identifier) -> bool:
        return self.components > other.components

    def __contains__(self, item: Identifier) -> bool:
        return self >= item

    def __hash__(self):
        return hash(tuple([subtype.tuple
                           for subtype in self._sorted_components]))

    def __repr__(self) -> str:  # noqa: D105
        try:
            return (f'{type(self).__name__}('
                    f'{self._rank_1}, {self._rank_2}, {self._rank_3}'
                    ')')
        except self.CompositeError:
            return ' | '.join(repr(id_)
                              for id_ in self._sorted_components)

    def __str__(self) -> str:  # noqa: D105
        try:
            return f'{self._rank_1}/{self._rank_2}/{self._rank_3}'
        except self.CompositeError:
            return '{' + ', '.join(str(id_)
                                   for id_ in self._sorted_components) + '}'

    @property
    def _sorted_components(self) -> List[Identifier]:
        return [type(self)(rank_1, rank_2, rank_3)
                for rank_1, subsection_tree in sorted(self._rank_1_map.items())
                for rank_2, rank_3_set in sorted(subsection_tree.items())
                for rank_3 in sorted(rank_3_set)]

    @classmethod
    def _from_components(cls, *components: Identifier) -> Identifier:
        """Build composite Identifier from components.

        Examples:
            >>> Identifier._from_components(Identifier(1, 2, 3),
            ...                             Identifier(1, 2, 4))
            Identifier(1, 2, 3) | Identifier(1, 2, 4)
        """
        composite_id = cls()
        composite_id._rank_1_map = cls._merge_ranks_1(
            *[type_._rank_1_map
              for type_ in components])
        return composite_id

    @classmethod
    def _merge_ranks_1(cls, *rank_1_maps: Rank1Map) -> Rank1Map:
        rank_1_maps = [deepcopy(map_) for map_ in rank_1_maps]
        common_keys = reduce(operator.and_,
                             (set(map_.keys()) for map_ in rank_1_maps))
        merged = {key: val
                  for map_ in rank_1_maps
                  for key, val in map_.items()}
        for key in common_keys:
            merged[key] = cls._merge_ranks_2(
                *[map_[key]
                  for map_ in rank_1_maps
                  if key in map_.keys()])
        return merged

    @classmethod
    def _merge_ranks_2(cls, *rank_2_maps: Rank2Map) -> Rank2Map:
        rank_2_maps = [deepcopy(map_) for map_ in rank_2_maps]
        common_keys = reduce(operator.and_,
                             (set(map_.keys()) for map_ in rank_2_maps))
        merged = {key: val
                  for map_ in rank_2_maps
                  for key, val in map_.items()}
        for key in common_keys:
            merged[key] = cls._merge_ranks_3(
                *[map_[key]
                  for map_ in rank_2_maps
                  if key in map_.keys()])
        return merged

    @classmethod
    def _merge_ranks_3(cls, *rank_3_sets: Rank3Set) -> Rank3Set:
        return reduce(operator.or_, rank_3_sets)

    class Error(Exception):
        """Base exception for Identifier identifier."""

    class CompositeError(Error):
        """Exeption related to composite Types."""


class Type(Identifier):
    """Identifie a data type."""

    Section = Optional[str]
    Subsection = Optional[str]
    FileFormat = Optional[str]

    def __init__(self,
                 section: Section = None,
                 subsection: Subsection = None,
                 file_format: FileFormat = None):
        super().__init__(rank_1=section,
                         rank_2=subsection,
                         rank_3=file_format)

    @property
    def section(self) -> Section:
        return self._rank_1

    @property
    def subsection(self) -> Subsection:
        return self._rank_2

    @property
    def file_format(self) -> FileFormat:
        return self._rank_3


class Sequence(Identifier):
    """Identifie a data sequence."""

    Road = Optional[int]
    Record = Optional[int]
    Camera = Optional[int]

    def __init__(self,
                 road: Road = None,
                 record: Record = None,
                 camera: Camera = None):
        super().__init__(rank_1=road,
                         rank_2=record,
                         rank_3=camera)

    @property
    def road(self) -> Road:
        return self._rank_1

    @property
    def record(self) -> Record:
        return self._rank_2

    @property
    def camera(self) -> Camera:
        return self._rank_3
