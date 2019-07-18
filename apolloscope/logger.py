# -*- coding: utf-8 -*-
"""This module provides logging helper functions.

Tip:
    The logging level values used in helper functions
    are the same as defined in the `logging module`_

.. _`logging module`:
        https://docs.python.org/3/library/logging.html#logging-levels

"""
import logging
import logging.handlers
import sys

from contextlib import contextmanager
from functools import wraps
from pathlib import Path
from time import time

__all__ = ['INDENT', 'INDENT_SIZE',
           'debug', 'info', 'warning', 'error', 'critical',
           'wrap_debug', 'wrap_info',
           'timer',
           'LoggingSetUp']

INDENT = True
"""bool: Control whether logs are indented."""
INDENT_SIZE = 4
"""int: Size of the log indentation."""

_DEFAULT_LOG_DIR = Path(__file__).parents[1] / 'logs'


class LoggingSetUp:
    """Logging set-up class for use when apolloscope is run as a script."""

    def __init__(self):
        self.formatter = None
        self.handlers = []
        self.logger = logging.getLogger()

    def add_console_output(self, log_level):
        """Make the logger display on terminal.

        Args:
            log_level (int): Logging level to filter

        """
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, log_level))
        console_handler.setFormatter(self.formatter)
        self.handlers.append(console_handler)

    def add_file_output(self,
                        log_level,
                        log_dir=_DEFAULT_LOG_DIR,
                        log_name='apolloscope'):
        # assert log_name is only a file name, without parent folder
        log_name = Path(log_name)
        if str(log_name) != log_name.name:
            raise ValueError(f'Invalid file name {log_name}')
        # create log directory
        log_dir.mkdir(parents=True, exist_ok=True)
        # enforce that logfile has .log extention
        if log_name.suffix != '.log':
            log_name = log_name.with_suffix(log_name.suffix + '.log')
        log_file = log_dir / log_name
        # add handler
        file_handler = logging.FileHandler(log_file, mode='w+')
        file_handler.setLevel(getattr(logging, log_level))
        file_handler.setFormatter(self.formatter)
        self.handlers.append(file_handler)

    def set_formatter(self, *args, **kwargs):
        self.formatter = logging.Formatter(*args, **kwargs)

    def apply(self):
        min_level = min([handler.level for handler in self.handlers])
        self.logger.setLevel(min_level)
        for handler in self.handlers:
            handler.setFormatter(self.formatter)
            self.logger.addHandler(handler)

    def default(self):
        self.add_console_output('INFO')
        self.add_file_output('DEBUG')
        self.set_formatter('[{levelname:>8}] {message} ({name})', style='{')
        self.apply()

########################################################################


class _Indentation:
    """Represent an indentation level.

    Attributes:
        size (int): Current indent level

    """

    def __init__(self, size=0):
        self.size = size

    def __str__(self):
        if INDENT:
            return self.size * INDENT_SIZE * ' '
        return ''

    def __add__(self, string):
        return str(self) + string

    def up(self):  # pylint: disable=C0103
        """Add one level to indentation."""
        self.size += 1

    def down(self):
        """Remove one level to indentation."""
        self.size -= 1


_indentation = _Indentation()  # pylint: disable=C0103
"""Global object defining the log indent level"""


def _caller_file_name(rank):
    frame = sys._getframe(0)  # pylint: disable=W0212
    for __ in range(rank):
        frame = frame.f_back
    return frame.f_globals['__name__']


@contextmanager
def timer(message='', log_level='debug', *, caller_rank=3):
    """Context manager for measuring execution time."""
    t_start = time()

    def get_time():
        return time() - t_start

    yield get_time
    if message:
        logger = logging.getLogger(_caller_file_name(caller_rank))
        log = getattr(logger, log_level)
        log(_indentation + message.format(get_time()))


def _make_logger(log_level):
    def logger(message='', *, caller_rank=2):
        logger = logging.getLogger(_caller_file_name(caller_rank))
        log = getattr(logger, log_level)
        log(f'{_indentation}{message}')
    return logger


def _make_log_wrapper(log_level, *, default_indent=True):
    """Produce decorator factories for a specific log level.

    Args:
        log_level (int): Logging level to filter
        default_indent (bool, optional): If set to False,
            logs made during the execution of the decorated function
            will not gain an additional indent level.
    """
    def log_wrapper(message='', *, indent=default_indent, caller_rank=2):

        def decorator(func):
            logger = logging.getLogger(_caller_file_name(caller_rank))
            log = getattr(logger, log_level)

            @wraps(func)
            def wrapped(*args, **kwargs):
                if not indent:
                    _indentation.down()

                log(f'{_indentation}Start {message.format(*args, **kwargs)}')
                _indentation.up()
                result = func(*args, **kwargs)
                _indentation.down()
                log(f'{_indentation}Done {message.format(*args, **kwargs)}')
                return result

            return wrapped

        return decorator

    return log_wrapper


# pylint: disable=C0103
debug = _make_logger('debug')
"""Log a message with a debug level."""

info = _make_logger('info')
"""Log a message with an info level."""

warning = _make_logger('warning')
"""Log a message with a warning level."""

error = _make_logger('error')
"""Log a message with an error level."""

critical = _make_logger('critical')
"""Log a message with a critical level."""

wrap_debug = _make_log_wrapper('debug', default_indent=False)
"""Log a message at the start and the end of a function's execution
with a debug level."""

wrap_info = _make_log_wrapper('info')
"""Log a message at the start and the end of a function's execution
with an info level."""
