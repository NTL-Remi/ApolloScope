# :mag: ApolloScope - ApolloScape dataset loading tool

[![ApolloScape][apolloscape_badge]][apolloscape_link]
[![Python version][python_version_badge]][python_version_link]
[![License][license_badge]][license_link]  
[![Documentation][documentation_badge]][documentation_link]  
![Build status][build_status_badge]
![Coverage][coverage_badge]  
![Pylint][pylint_badge]


**WIP - Version 0**

This is a Python package for visualisation and loading of Baidu's ApolloScape data-set for vehicle vision tasks.

Currently it is only focused on the overlapping [__Lane segmentation__][lane_segmentation] and [__Scene parsing__][scene_parsing] data-sets.

## temporary usage

Currently this project is still a bit messy. I plan on cleaning it and
improving the UI (probably inducing some heavy changes) when I will have some
time.
Here is some code if you want to use it in its current state:

```python
import apolloscope
from apolloscope.ls_sp.register import Register, SequenceId, TypeId
```
Specify  the paths to the data-set:
```python
sp_path = PATH_TO_YOUR_SCENE_PARSING_FOLDER
ls_path = PATH_TO_YOUR_LANE_SEGMENTATION_FOLDER

apolloscope.root_folder.scene_parsing(sp_path)
apolloscope.root_folder.lane_segmentation(ls_path)
```
The expected folder architecture is the one used in ApolloScape archive files.
Some archives seem to have been zipped differently than others and will not 
recreate the top-most folder (the one that has the same name as the archive), 
you will have to create it yourself (this is for example the case for the scene 
parsing `road02_seg_depth.tar.gz` file).

This will parse the file paths in the specified folders and classifying
them by image type and sequence in a multi-indexed data-frame (see it like a 2D
array in which we are going to slice depending on the data we want):
```python
register = Register()
```
Say that we want to iterate at the same time on the colour data, the semantic
segmentation and the depth maps. We define the three data types:
```python
image_type = TypeId(dataset="SP",
                    section="seg",
                    subsection="ColorImage",
                    file_type="jpg")
depth_type = TypeId("SP", "seg_depth", "Depth", "png")
seg_type = TypeId("SP", "seg", "Label", "bin.png")
```
Suppose that we want to iterate over the frames captured on road 2,
sequence 22, camera 5. We define the sequence:
```python
test_sequence = SequenceId(road=2, record=22, camera=5)
```
In both data types and sequences definition, all parameters are optional,
allowing to select larger parts of the data-set. Defining
```python
test_sequence = SequenceId(road=2, camera=5)
```
will take the data of all records on road 2 filmed by camera 5.

To actually select the data from `register`, we do:
```python
filtered_register = register.types([file_type, depth_type, seg_type])
filtered_register = filtered_register.sequences([test_sequence])
```
We can then get the Pytorch dataset:
```python
dataset = apolloscope.ls_sp.pytorch.Dataset(filtered_register)
```
and use it in a pytorch dataloader in a classical way.
In the current case, each element would be a tuple of three images
corresponding to the three data types we defined, at a same time-stamp.
Triplets with missing data would be dropped.

[lane_segmentation]: http://apolloscape.auto/lane_segmentation.html
[scene_parsing]: http://apolloscape.auto/scene.html

[apolloscape_badge]: https://badgen.net/badge/ApolloScape/ApolloScape?icon=https://simpleicons.now.sh/baidu/fff&label&color=black
[apolloscape_link]: http://apolloscape.auto

[documentation_badge]: https://badgen.net/badge/github/Documentation?icon=https://simpleicons.now.sh/readthedocs/fff&label&color=blue
[documentation_link]: https://ntl-remi.github.io/ApolloScope/build/html/index.html

[license_badge]: https://badgen.net/badge/License/LGPL?color=purple
[license_link]: https://github.com/NTL-Remi/ApolloScope/blob/master/LICENSE.md

[python_version_badge]: https://badgen.net/badge/Python/3.7?icon=https://simpleicons.now.sh/python/fff&color=blue
[python_version_link]: https://www.python.org/downloads/release/python-373/

[build_status_badge]: https://travis-ci.org/NTL-Remi/ApolloScope.svg?branch=master

[coverage_badge]: ./docs/source/_static/badges/coverage.svg

[pylint_badge]: ./docs/source/_static/badges/pylint.svg
