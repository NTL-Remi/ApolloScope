import enum

from anytree import AnyNode


class TypeTree:

    def __init__(self, mapping):
        self._root = AnyNode(level=self.Level.ROOT)
        for section, subsections in mapping.items():
            section_node = AnyNode(parent=self._root,
                                   value=section,
                                   level=self.Level.SECTION)
            for subsection, file_types in subsections.items():
                subsection_node = AnyNode(parent=section_node,
                                          value=subsection,
                                          level=self.Level.SUBSECTION)
                for file_type in file_types:
                    AnyNode(parent=subsection_node,
                            value=file_type,
                            level=self.Level.FILE_TYPE)

    class Level(enum.Enum):
        ROOT = enum.auto()
        SECTION = enum.auto()
        SUBSECTION = enum.auto()
        FILE_TYPE = enum.auto()
