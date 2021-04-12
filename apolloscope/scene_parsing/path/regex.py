"""Regular expressions

To sort all files in the dataset, we need to identify their content.
In appoloscape, it is only possible through the file's name and location.
Here we define regexes to extract relevant infos from the files' paths.
"""
import os
import re

SEPARATOR = re.escape(os.path.sep)
"""str: Regex-escaped path separator for current OS."""

FOLDER = SEPARATOR.join(
    [r'\w*',
     r'road(?P<road>\d+)_(?P<section>\w+?)',
     r'(?P<subsection>\w+?)',
     r'Record(?P<record>\d+)',
     r'Camera (?P<camera>\d+)'])
"""str: regex for scene parsing dataset folders."""

FILE_DATED = re.compile(SEPARATOR.join(
    [FOLDER,
     r'\d+_(?P<date>\d+)_'
     r'Camera_(?P=camera)[_.]'
     r'(?P<file_type>[.\w]+?)$']))
"""re.Pattern: Compiled regex for scene parsing dataset regular files."""

FILE_POSE = re.compile(SEPARATOR.join(
    [FOLDER,
     r'pose\.(?P<file_type>txt)$']))
"""re.Pattern: Compiled regex for scene parsing dataset pose files."""
