from __future__ import annotations

import operator
from copy import deepcopy
from functools import reduce
from typing import List, Mapping, Optional, Set


class Type:
    """Apolloscape datatype representation."""

    Section = Optional[str]
    Subsection = Optional[str]
    FileFormat = Optional[str]

    FileFormatSet = Set[FileFormat]
    SubsectionTree = Mapping[Subsection, FileFormatSet]
    SectionTree = Mapping[Section, SubsectionTree]

    def __init__(self,
                 section: Section = None,
                 subsection: Subsection = None,
                 file_format: FileFormat = None):

        self._section_tree: Type.SectionTree = {section:
                                                {subsection:
                                                 {file_format}}}

    @property
    def subtypes(self) -> Set[Type]:
        """Return the set of composing elementary types.

        Exemples:
            TODO
        """
        return set(self._sorted_subtypes())

    @property
    def is_composite(self) -> bool:
        """Is True if the datatype includes multiple component subtypes.

        Examples:
            TODO: true names
            >>> simple_type = Type('1', '2', '3')
            >>> simple_type.is_composite
            False
            >>> composite_type = Type('1', '2', '3') | Type('11', '12', '13')
            >>> composite_type.is_composite
            True
        """
        return len(self.subtypes) > 1

    @property
    def is_definite(self) -> bool:
        """Is True if the datatype does not have catch-all fields.

        Examples:
            TODO: true names
            >>> definite_type = Type('1', '2', '3')
            >>> definite_type.is_definite
            True
            >>> undefinite_type = Type('1', 'None', '3')
            >>> undefinite_type.is_definite
            False
        """
        try:
            return (self.section is not None
                    and self.subsection is not None
                    and self.file_format is not None)
        except self.CompositeError:
            return any(subtype.is_composite for subtype in self.subtypes)

    @property
    def section(self) -> Section:
        """Return the Type section if it is not composite.

        Raise:
            Type.CompositeError: The Type has more than one section.

        Exemples:
            TODO: true names
            >>> simple_type = Type('1', '2', '3')
            >>> simple_type.section
            1
            >>> composite_type = Type('1', '2', '3') | Type('11', '12', '13')
            >>> composite_type.section
            Traceback (most recent call last):
            CompositeError: Type.section is undefined
        """
        try:
            if len(self._section_tree) > 1:
                raise self.CompositeError('Type has multiple sections')
        except self.CompositeError as err:
            raise self.CompositeError('Type.section is undefined') from err
        return list(self._section_tree.keys())[0]

    @property
    def subsection(self) -> Subsection:
        """Return the Type subsection if it is not composite.

        Raise:
            Type.CompositeError: The Type has more than one section
                or more than one subsection.

        Exemples:
            TODO
        """
        try:
            subsection_tree = self._section_tree[self.section]
            if len(subsection_tree) > 1:
                raise self.CompositeError('Type has multiple subsections')
        except self.CompositeError as err:
            raise self.CompositeError('Type.subsection is undefined') from err
        return list(subsection_tree.keys())[0]

    @property
    def file_format(self) -> FileFormat:
        """Return the Type file format if it is not composite.

        Raise:
            Type.CompositeError: The Type has more than one section
                or more than one subsection
                or more than one file format.

        Exemples:
            TODO
        """
        try:
            file_format_set = self._section_tree[self.section][self.subsection]
            if len(file_format_set) > 1:
                raise self.CompositeError('Type has multiple file formats')
        except self.CompositeError as err:
            raise self.CompositeError('Type.file_format is undefined') from err
        return list(file_format_set)[0]

    @property
    def tuple(self):
        try:
            return (self.section, self.subsection, self.file_format)
        except self.CompositeError as err:
            raise self.CompositeError('Not representable as a tuple') from err

    def __or__(self, other: Type) -> Type:  # noqa: D105
        return Type._from_subtypes(self, other)

    def __add__(self, other: Type) -> Type:  # noqa: D105
        return self | other

    def __eq__(self, other: Type) -> bool:
        return self._section_tree == other._section_tree

    def __le__(self, other: Type) -> bool:
        """Test whether every subtype in self is in other."""
        return self.subtypes <= other.subtypes

    def __ge__(self, other: Type) -> bool:
        """Test whether every subtype in other is in self."""
        return self.subtypes >= other.subtypes

    def __lt__(self, other: Type) -> bool:
        return self.subtypes < other.subtypes

    def __gt__(self, other: Type) -> bool:
        return self.subtypes > other.subtypes

    def __contains__(self, item: Type) -> bool:
        return self >= item

    def __hash__(self):
        return hash(tuple([subtype.tuple
                           for subtype in self._sorted_subtypes()]))

    def __repr__(self) -> str:  # noqa: D105
        try:
            return ('Type('
                    f'{self.section}, {self.subsection}, {self.file_format}'
                    ')')
        except self.CompositeError:
            return ' | '.join(repr(type_) for type_ in self.subtypes)

    def __str__(self) -> str:  # noqa: D105
        try:
            return '/'.join([self.section, self.subsection, self.file_format])
        except self.CompositeError:
            return '{' + ', '.join(str(type_) for type_ in self.subtypes) + '}'

    def _sorted_subtypes(self) -> List[Type]:
        return [
            Type(section=section,
                 subsection=subsection,
                 file_format=file_format)
            for section, subsection_tree in sorted(self._section_tree.items())
            for subsection, file_format_set in sorted(subsection_tree.items())
            for file_format in sorted(file_format_set)]

    @staticmethod
    def _from_subtypes(*subtypes: Type) -> Type:
        composite_type = Type()
        composite_type._section_tree = Type._merge_sections(
            *[type_._section_tree
              for type_ in subtypes])
        return composite_type

    @staticmethod
    def _merge_sections(*section_maps: SectionTree) -> SectionTree:
        section_maps = [deepcopy(map_) for map_ in section_maps]
        common_keys = reduce(operator.and_,
                             (set(map_.keys()) for map_ in section_maps))
        merged = {key: val
                  for map_ in section_maps
                  for key, val in map_.items()}
        for key in common_keys:
            merged[key] = Type._merge_file_formats(
                *[map_[key]
                  for map_ in section_maps
                  if key in map_.keys()])
        return merged

    @staticmethod
    def _merge_subsections(*subsection_maps: SubsectionTree) -> SubsectionTree:
        subsection_maps = [deepcopy(map_) for map_ in subsection_maps]
        common_keys = reduce(operator.and_,
                             (set(map_.keys()) for map_ in subsection_maps))
        merged = {key: val
                  for map_ in subsection_maps
                  for key, val in map_.items()}
        for key in common_keys:
            merged[key] = Type._merge_file_formats(
                *[map_[key]
                  for map_ in subsection_maps
                  if key in map_.keys()])
        return merged

    @staticmethod
    def _merge_file_formats(*file_format_sets: FileFormatSet) -> FileFormatSet:
        return reduce(operator.or_, file_format_sets)

    class Error(Exception):
        """Base exception for Type identifier."""

    class CompositeError(Error):
        """Exeption related to composite Types."""
