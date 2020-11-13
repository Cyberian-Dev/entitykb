"""
Copyright © 2018, Encode OSS Ltd. All rights reserved.

Original Code:
    https://github.com/encode/starlette/blob/master/starlette/config.py
"""


import os
import typing

from collections.abc import MutableMapping


class EnvironError(Exception):
    pass


class CheckEnviron(MutableMapping):
    class DEFAULTS:
        pass

    def __init__(self, _environ: typing.MutableMapping = os.environ):
        self._environ = _environ
        self._has_been_read: typing.Set = set()

    def __getitem__(self, key: typing.Any) -> typing.Any:
        self._has_been_read.add(key)
        value = self._environ.get(key)
        if value is None:
            value = getattr(self.DEFAULTS, key, None)
            if value:
                self._environ.__setitem__(key, str(value))
        return value

    def __setitem__(self, key: typing.Any, value: typing.Any) -> None:
        if value is None:
            return
        if key in self._has_been_read:
            raise EnvironError(f"Setting previously read environ['{key}']")
        self._environ.__setitem__(key, value)

    def __delitem__(self, key: typing.Any) -> None:
        if key in self._has_been_read:
            raise EnvironError(f"Deleting previously read environ['{key}']")
        self._environ.__delitem__(key)

    def __iter__(self) -> typing.Iterator:
        return iter(self._environ)

    def __len__(self) -> int:
        return len(self._environ)
