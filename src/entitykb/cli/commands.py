from pathlib import Path
from typing import Optional

import typer
import uvicorn
from tabulate import tabulate

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
def reset(root: Optional[Path] = typer.Option(None)):
    """ Reset local KB """

    root = Config.get_root(root)
    typer.confirm(f"Are you sure you want to reset: {root}?", abort=True)

    kb = KB(root=root)
    success = kb.reset()
    finish("Reset", success)


@cli.command()
def info(root: Optional[Path] = typer.Option(None)):
    """ Display information for local KB """
    kb = KB(root=root)
    flat = sorted(services.flatten_dict(kb.info()).items())
    output = tabulate(flat, tablefmt="pretty", colalign=("left", "right"))
    typer.echo(output)


@cli.command()
def load(
    root: Optional[Path] = typer.Option(None),
    in_file: Path = typer.Argument(None),
    format: services.FileFormat = services.FileFormat.csv,
    dry_run: bool = typer.Option(False, "--dry-run"),
):
    """ Load data into local KB """

    if not dry_run:
        kb = KB(root=root)
    else:
        kb = services.PreviewKB(length=10)

    file_obj = in_file.open("r")
    it = services.iterate_entities(file_obj=file_obj, file_format=format)

    total = 0
    with typer.progressbar(it) as progress:
        for entity in progress:
            kb.save_node(entity)
            total += 1

    kb.commit()


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
    environ.root = root
    environ.rpc_host = host
    environ.rpc_port = rpc_port

    http_app = "entitykb.http.dev:app"
    uvicorn.run(http_app, host=host, port=http_port, reload=True)


if __name__ == "__main__":
    cli()
