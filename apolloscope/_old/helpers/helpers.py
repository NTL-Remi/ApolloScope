# -*- coding: utf-8 -*-
from collections import deque
from pathlib import Path

from .. import logger


@logger.wrap_debug('searching for target {1} in {0}', indent=True)
def path_bfs(root, target):
    """Search for a file path with breadth-first priority."""
    root = Path(root)
    assert root.exists() and root.is_dir()

    queue = deque([root])
    while queue:
        folder = queue.pop()
        try:
            for sub_file in folder.iterdir():
                if sub_file.match(target):
                    logger.debug(f'found target at {sub_file}')
                    return sub_file
                if sub_file.is_dir():
                    queue.appendleft(sub_file)
        except PermissionError as err:
            logger.debug(f'ignoring {folder}: {err.strerror}')
    logger.warning(f'target {target} not found in {root}')
    return None
