import os
import shutil
from pathlib import Path
from typing import Optional

import typer
import uvicorn
import time

from tabulate import tabulate
from io import FileIO

from entitykb import KB, Config, logger, environ, rpc
from . import services

cli = typer.Typer()


def finish(operation: str, success: bool, error_code: int = None):
    if success:
        logger.info(f"{operation} completed successfully.")
    else:
        logger.warning(f"{operation} failed.")
        raise typer.Exit(error_code or 1)


@cli.command()
def init(root: Optional[Path] = typer.Option(None)):
    """ Initialize local KB """
    success = services.init_kb(root=root, exist_ok=True)
    finish("Initialization", success)


@cli.command()
def clear(root: Optional[Path] = typer.Option(None)):
    """ Clear local KB """

    root = Config.get_root(root)
    path = os.path.join(root, "index.db")
    typer.confirm(f"Are you sure you want to clear: {path}?", abort=True)

    os.remove(path)

    kb = KB(root=root)
    success = kb.commit()

    finish("Clear", success)


@cli.command()
def info(root: Optional[Path] = typer.Option(None)):
    """ Display information for local KB """
    kb = KB(root=root)
    flat = sorted(services.flatten_dict(kb.info()).items())
    output = tabulate(flat, tablefmt="pretty", colalign=("left", "right"))
    typer.echo(output)


@cli.command()
def load(
    in_file: Path = typer.Argument(None),
    root: Optional[Path] = typer.Option(None),
    format: str = typer.Option("csv"),
    dry_run: bool = typer.Option(False, "--dry-run"),
    mv_split: str = typer.Option("|"),
):
    """ Load data into local KB """
    start = time.time()
    environ.mv_split = mv_split

    kb = KB(root=root) if not dry_run else None

    file_obj = in_file.open("r")
    it = iterate_file(file_format=format, file_obj=file_obj)

    count = 0
    with typer.progressbar(it) as progress:
        for obj in progress:
            if kb:
                kb.save(obj)
            elif count < 10:
                typer.echo(obj)
            count += 1

    if kb:
        kb.commit()
        timer = time.time() - start
        typer.echo(f"Loaded {count} in {timer:.2f}s [{in_file}, {format}]")


@cli.command(name="rpc")
def run_rpc(
    root: Optional[Path] = typer.Option(None),
    host: Optional[str] = typer.Option(None),
    port: int = typer.Option(None),
):
    """ Launch RPC server using local KB """

    rpc.launch(root=root, host=host, port=port)


@cli.command(name="http")
def run_http(
    root: Optional[Path] = typer.Option(None),
    host: Optional[str] = typer.Option(None),
    port: int = typer.Option(None),
    http_host: Optional[str] = typer.Option(None),
    rpc_port: int = typer.Option(3477),
):
    """ Launch HTTP server using RPC KB. """
    environ.root = root
    environ.rpc_host = http_host
    environ.rpc_port = rpc_port

    http_app = "entitykb.http.prod:app"
    uvicorn.run(http_app, host=host, port=port, reload=True)


@cli.command(name="dev")
def run_dev(
    root: Optional[Path] = typer.Option(None),
    host: str = typer.Option("127.0.0.1"),
    rpc_port: int = typer.Option(3477),
    http_port: int = typer.Option(8000),
):
    """ Hot reloading local HTTP and RPC servers. """

    # set environment variables
    # commit to os.environ for HTTP/RPC processes
    environ.root = root
    environ.rpc_host = host
    environ.rpc_port = rpc_port
    environ.commit()

    # check working directory and the entitykb directory
    reload_dirs = [os.getcwd(), os.path.dirname(os.path.dirname(__file__))]

    http_app = "entitykb.http.dev:app"
    uvicorn.run(
        http_app,
        host=host,
        port=http_port,
        reload=True,
        reload_dirs=reload_dirs,
    )


ff_registry = {}


def register_format(file_format: str):
    def decorator_register(func):
        assert file_format not in ff_registry, f"Duplicate: {file_format}"
        ff_registry[file_format] = func
        return func

    return decorator_register


def iterate_file(file_format: str, file_obj: FileIO):
    func = ff_registry[file_format]
    yield from func(file_obj)


cli.register_format = register_format
