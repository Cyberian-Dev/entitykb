import os
import time
import json

from inspect import getfullargspec
from io import FileIO
from pathlib import Path
from typing import Optional

import typer
import smart_open
import uvicorn
from tabulate import tabulate
from pydantic.json import pydantic_encoder

from entitykb import KB, Config, logger, environ, rpc, Direction
from . import services

cli = typer.Typer(add_completion=False)


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
def clear(
    root: Optional[Path] = typer.Option(None),
    force: bool = typer.Option(False, "--force", "-f"),
):
    """ Clear local KB """

    root = Config.get_root(root)
    path = root / "index.db"

    if os.path.exists(path):
        if not force:
            typer.confirm(f"Clearing {path}. Are you sure?", abort=True)
        os.remove(path)
    else:
        logger.info(f"{path} does not exist. Creating new database.")

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
def dump(
    output: str = typer.Argument("-"),
    root: Optional[Path] = typer.Option(None),
):
    """ Dump data from KB in JSONL format. """
    with typer.open_file(output, "w") as f:
        kb = KB(root=root)
        for node in kb.graph:
            payload = node.dict()
            envelope = dict(kind="node", payload=payload)
            data = json.dumps(envelope, default=pydantic_encoder)
            f.write(data)
            f.write("\n")

            it = kb.graph.iterate_edges(
                directions=Direction.outgoing, nodes=node
            )

            for _, edge in it:
                payload = edge.dict()
                envelope = dict(kind="edge", payload=payload)
                data = json.dumps(envelope, default=pydantic_encoder)
                f.write(data)
                f.write("\n")


@cli.command()
def load(
    in_file: str = typer.Argument(None),
    root: Optional[Path] = typer.Option(None),
    format: str = typer.Option("jsonl"),
    dry_run: bool = typer.Option(False, "--dry-run"),
    mv_split: str = typer.Option("|"),
):
    """ Load data into local KB """
    start = time.time()
    environ.mv_split = mv_split

    kb = KB(root=root) if not dry_run else None

    file_obj = smart_open.open(in_file)
    it = iterate_file(file_format=format, file_obj=file_obj, kb=kb)

    count = 0
    with typer.progressbar(it) as progress:
        for obj in progress:
            count += 1

            if kb:
                kb.save(obj)
            elif count <= 10:
                typer.echo(obj)

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
    host: Optional[str] = typer.Option("127.0.0.1"),
    port: int = typer.Option(8000),
    rpc_host: Optional[str] = typer.Option("127.0.0.1"),
    rpc_port: int = typer.Option(3477),
):
    """ Launch HTTP server using RPC KB. """
    environ.root = root
    environ.rpc_host = rpc_host
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


def iterate_file(file_format: str, file_obj: FileIO, kb: KB):
    func = ff_registry[file_format]
    spec = getfullargspec(func)
    if len(spec.args) == 1:
        yield from func(file_obj)
    elif len(spec.args) == 2:
        yield from func(file_obj, kb)
    else:
        raise RuntimeError(f"Invalid reader function: {func} {spec.args}")


cli.register_format = register_format
