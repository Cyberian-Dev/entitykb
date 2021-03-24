from inspect import getfullargspec
from io import FileIO
from typing import List

import typer

from entitykb import KB


class CustomTyper(typer.Typer):
    def __init__(self, *, add_completion=False, **kwargs):
        self.reader_registry = {}
        self.writer_registry = {}
        super().__init__(add_completion=add_completion, **kwargs)

    def get_reader(
        self, file_format, file_obj: FileIO, kb: KB, flags: List[str] = None
    ):
        reader = self.reader_registry[file_format]
        spec = getfullargspec(reader)

        assert 1 <= len(spec.args) <= 3, f"Invalid reader function: {reader}"
        args = [file_obj, kb, flags]
        args = args[: len(spec.args)]

        yield from reader(*args)

    def register_reader(self, file_format: str):
        def decorator_register(func):
            assert (
                file_format not in self.reader_registry
            ), f"Duplicate Reader Format: {file_format}"
            self.reader_registry[file_format] = func
            return func

        return decorator_register

    def get_writer(self, file_format: str):
        return self.writer_registry[file_format]

    def register_writer(self, file_format: str):
        def decorator_register(func):
            assert (
                file_format not in self.writer_registry
            ), f"Duplicate Writer Format: {file_format}"
            self.writer_registry[file_format] = func
            return func

        return decorator_register


cli = CustomTyper()
