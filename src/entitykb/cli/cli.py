import typer
from inspect import getfullargspec
from io import FileIO
from entitykb import KB


class CustomTyper(typer.Typer):
    def __init__(self, *, add_completion=False, **kwargs):
        self.reader_registry = {}
        self.writer_registry = {}
        super().__init__(add_completion=add_completion, **kwargs)

    def get_reader(self, file_format: str, file_obj: FileIO, kb: KB):
        reader = self.reader_registry[file_format]
        spec = getfullargspec(reader)

        if len(spec.args) == 1:
            yield from reader(file_obj)
        elif len(spec.args) == 2:
            yield from reader(file_obj, kb)
        else:
            raise RuntimeError(f"Invalid function: {reader} {spec.args}")

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
