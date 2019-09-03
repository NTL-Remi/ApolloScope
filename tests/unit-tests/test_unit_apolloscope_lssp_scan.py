# -*- coding: utf-8 -*-
"""This modules declares unit tests for the apolloscope.lssp module."""
# pylint: disable = no-value-for-parameter
import itertools as it
import string
import unittest
from unittest import mock

from hypothesis import given
from hypothesis import strategies as st

from apolloscope.ls_sp import scan

# define strategy shortcuts
NUM_STRING = st.text(alphabet=string.digits, min_size=1)
"""Generate numerical strings."""

ALPHA_STRING = st.text(alphabet=string.ascii_letters, min_size=1)
"""Generate alphabetical strings."""

ALPHA_POINT_STRING = st.text(alphabet=string.ascii_letters + '.', min_size=1)
"""Generate alphabetical strings."""

EXTENTION_SEPARATOR = st.sampled_from('._')
"""Generate extention separator characters."""


def strings_from_regex(regex):
    """Generate lists of strings matching a given regex."""
    return st.lists(st.from_regex(regex, fullmatch=True),
                    min_size=1,
                    unique=True)


# strategies
@st.composite
def ls_path_and_capture_groups(draw):
    """Generate random ls paths and their capture groups.

    Paths are generated following the expected structure
    of the lane segmentation dataset.
    """
    road = draw(NUM_STRING)
    record = draw(NUM_STRING)
    camera = draw(NUM_STRING)
    date = draw(NUM_STRING)
    section = draw(ALPHA_STRING)
    subsection = draw(ALPHA_STRING)
    file_type = draw(ALPHA_POINT_STRING)
    ext_sep = draw(st.sampled_from('._'))
    return (f'root_folder/'
            f'{section}_road{road}/'
            f'{subsection}/'
            f'Record{record}/'
            f'Camera {camera}/'
            f'12345_{date}_Camera_{camera}{ext_sep}{file_type}',
            (section, road, subsection, record, camera, date, file_type))


@st.composite
def sp_dated_path_and_capture_groups(draw):
    """Generate random sp dated paths and their capture groups.

    Paths are generated following the expected structure
    of the scene parsing dataset for date-specific files
    (i.e. non-pose files).
    """
    road = draw(NUM_STRING)
    record = draw(NUM_STRING)
    camera = draw(NUM_STRING)
    date = draw(NUM_STRING)
    section = draw(ALPHA_STRING)
    subsection = draw(ALPHA_STRING)
    file_type = draw(ALPHA_POINT_STRING)
    ext_sep = draw(st.sampled_from('._'))
    return (f'root_folder/'
            f'road{road}_{section}/'
            f'{subsection}/'
            f'Record{record}/'
            f'Camera {camera}/'
            f'12345_{date}_Camera_{camera}{ext_sep}{file_type}',
            (road, section, subsection, record, camera, date, file_type))


@st.composite
def sp_pose_path_and_capture_groups(draw):
    """Generate random sp pose paths and their capture groups.

    Paths are generated following the expected structure
    of the scene parsing dataset for pose files.
    """
    road = draw(NUM_STRING)
    record = draw(NUM_STRING)
    camera = draw(NUM_STRING)
    section = draw(ALPHA_STRING)
    return (f'root_folder/'
            f'road{road}_{section}/'
            f'Pose/'
            f'Record{record}/'
            f'Camera {camera}/'
            f'pose.txt',
            (road, section, 'Pose', record, camera, 'txt'))


class TestRegexes(unittest.TestCase):
    """Test the correctness of the regexes group captures."""

    @given(ls_path_and_capture_groups())
    def test_ls_file_regex(self, path_and_capture):
        path, capture = path_and_capture
        match = scan.LS_FILE_REGEX.fullmatch(path)
        print(path)
        print(scan.LS_FILE_REGEX.pattern)
        print(capture)
        assert match.groups() == capture

    @given(sp_dated_path_and_capture_groups())
    def test_sp_dated_file_regex(self, path_and_capture):
        path, capture = path_and_capture
        match = scan.SP_DATED_FILE_REGEX.fullmatch(path)
        assert match.groups() == capture

    @given(sp_pose_path_and_capture_groups())
    def test_sp_pose_file_regex(self, path_and_capture):
        path, capture = path_and_capture
        match = scan.SP_POSE_FILE_REGEX.fullmatch(path)
        assert match.groups() == capture


class TestScaners(unittest.TestCase):

    @given(strings_from_regex(scan.LS_FILE_REGEX))
    def test_lane_segmentation_scan(self, paths):
        with mock.patch('pathlib.Path.glob', return_value=paths), \
             mock.patch('pathlib.Path.exists', return_value=True):
            dataframe = scan.lane_segmentation('')
            assert sorted(paths) == sorted(dataframe['path'])

    @given(strings_from_regex(scan.SP_DATED_FILE_REGEX),
           strings_from_regex(scan.SP_POSE_FILE_REGEX))
    def test_scene_parsing_scan(self, dated_paths, pose_paths):
        paths = dated_paths + pose_paths
        with mock.patch('pathlib.Path.glob', return_value=paths), \
                mock.patch('pathlib.Path.exists', return_value=True):
            dataframe = scan.scene_parsing('')
            assert sorted(dated_paths) == sorted(dataframe['path'])


if __name__ == '__main__':
    unittest.main()
