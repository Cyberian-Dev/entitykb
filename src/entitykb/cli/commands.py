import os
import time
from pathlib import Path
from typing import Optional

import smart_open
import typer
import uvicorn
from tabulate import tabulate

from entitykb import KB, Config, environ, rpc, Direction
from . import cli, services


@cli.command()
def init(root: Optional[Path] = typer.Option(None)):
    """ Initialize local KB """
    success = services.init_kb(root=root, exist_ok=True)
    services.finish("Initialization", success)


@cli.command()
def clear(
    root: Optional[Path] = typer.Option(None),
    force: bool = typer.Option(False, "--force", "-f"),
):
    """ Clear local KB """

    root = Config.get_root(root)

    if root.exists():
        if not force:
            typer.confirm(f"Clearing {root}. Are you sure?", abort=True)

    kb = KB(root=root)
    kb.clear()
    services.finish("Clear", True)


@cli.command()
def info(root: Optional[Path] = typer.Option(None)):
    """ Display information for local KB """
    kb = KB(root=root)
    flat = sorted(services.flatten_dict(kb.info()).items())
    output = tabulate(flat, tablefmt="pretty", colalign=("left", "right"))
    typer.echo(output)


@cli.command()
def dump(
    out_file: str = typer.Argument("-"),
    root: Optional[Path] = typer.Option(None),
    file_format: str = typer.Option("jsonl", "--ff"),
):
    """ Dump data from KB in JSONL format """
    if out_file == "-":
        file_obj = typer.open_file(out_file, mode="w")
    else:
        file_obj = smart_open.open(out_file, mode="w")

    kb = KB(root=root)
    writer = cli.get_writer(file_format=file_format)

    for node in kb:
        writer(file_obj, node)

        it = kb.graph.iterate_edges(directions=Direction.outgoing, nodes=node)
        for _, edge in it:
            writer(file_obj, edge)


@cli.command()
def load(
    in_file: str = typer.Argument(None),
    root: Optional[Path] = typer.Option(None),
    file_format: str = typer.Option("jsonl", "--ff"),
    dry_run: bool = typer.Option(False, "--dry-run"),
    skip_reindex: bool = typer.Option(False, "--skip-reindex"),
    is_binary: bool = typer.Option(False, "--is_binary"),
):
    """ Load data into local KB """
    t0 = time.time()

    kb = KB(root=root)
    typer.echo(f"Loading using {file_format} from {in_file}")

    mode = "rb" if is_binary else "r"
    if in_file == "-":
        file_obj = typer.open_file(in_file, mode=mode)
    else:
        file_obj = smart_open.open(in_file, mode=mode)

    reader = cli.get_reader(file_format, file_obj=file_obj, kb=kb)

    count = 0
    with typer.progressbar(reader) as progress:
        with kb.transact():
            for obj in progress:
                count += 1

                if not dry_run:
                    kb.save(obj)
                elif count <= 10:
                    typer.echo(obj)
                else:
                    break

    t1 = time.time()
    typer.echo(f"Loaded {count} in {t1 - t0:.2f}s [{in_file}, {file_format}]")
    if not dry_run and not skip_reindex:
        reindex(root=root)


@cli.command()
def reindex(root: Optional[Path] = typer.Option(None)):
    """ Load data into local KB """
    t0 = time.time()
    kb = KB(root=root)
    typer.echo(f"Reindexing {kb.config.root}...")

    kb.reindex()
    t1 = time.time()
    typer.echo(f"Reindexed {kb.config.root} in {t1 - t0:.2f}s")


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
    reload: bool = typer.Option(False),
):
    """ Launch HTTP server using RPC KB """
    environ.root = root
    environ.rpc_host = rpc_host
    environ.rpc_port = rpc_port

    http_app = "entitykb.http.prod:app"
    uvicorn.run(http_app, host=host, port=port, reload=reload)


@cli.command(name="dev")
def run_dev(
    root: Optional[Path] = typer.Option(None),
    host: str = typer.Option("127.0.0.1"),
    rpc_port: int = typer.Option(3477),
    http_port: int = typer.Option(8000),
):
    """ Hot reloading local HTTP and RPC servers """

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
