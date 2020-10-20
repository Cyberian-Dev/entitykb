from pathlib import Path
from typing import Optional

import typer
from tabulate import tabulate

from entitykb import KB, Config, logger
from entitykb.http import launch_http
from entitykb.rpc import launch_rpc
from . import services

app = typer.Typer()


def finish(operation: str, success: bool, error_code: int = None):
    if success:
        logger.info(f"{operation} completed successfully.")
    else:
        logger.warning(f"{operation} failed.")
        raise typer.Exit(error_code or 1)


@app.command()
def init(root: Optional[Path] = typer.Option(None)):
    """ Initialize local KB """
    success = services.init_kb(root=root, exist_ok=True)
    finish("Initialization", success)


@app.command()
def reset(root: Optional[Path] = typer.Option(None)):
    """ Reset local KB """

    root = Config.get_root(root)
    typer.confirm(f"Are you sure you want to reset: {root}?", abort=True)

    kb = KB(root=root)
    success = kb.reset()
    finish("Reset", success)


@app.command()
def info(root: Optional[Path] = typer.Option(None)):
    """ Display information for local KB """
    kb = KB(root=root)
    flat = sorted(services.flatten_dict(kb.info()).items())
    output = tabulate(flat, tablefmt="pretty", colalign=("left", "right"))
    typer.echo(output)


@app.command()
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


@app.command()
def rpc(
    root: Optional[Path] = typer.Option(None),
    host: Optional[str] = typer.Option(None),
    port: int = typer.Option(None),
):
    """ Launch RPC server calling local KB """
    launch_rpc(root=root, host=host, port=port)


@app.command()
def http():
    """ Launch HTTP server calling RPC server """
    launch_http()


if __name__ == "__main__":
    app()
