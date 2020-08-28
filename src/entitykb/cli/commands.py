from pathlib import Path
from typing import Optional

import typer
from tabulate import tabulate

from entitykb import KB, Config, logger, utils
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
def init(root_dir: Optional[Path] = typer.Argument(None)):
    success = services.init_kb(root_dir=root_dir)
    finish("Initialization", success)


@app.command()
def reset(root_dir: Optional[Path] = typer.Argument(None)):
    root_dir = Config.get_root_dir(root_dir)
    typer.confirm(f"Are you sure you want to reset: {root_dir}?", abort=True)
    success = services.reset_kb(root_dir=root_dir)
    finish("Reset", success)


@app.command()
def info(root_dir: Optional[Path] = typer.Argument(None)):
    kb = KB(root_dir=root_dir)
    flat = sorted(utils.flatten_dict(kb.info()).items())
    output = tabulate(flat, tablefmt="pretty", colalign=("left", "right"))
    typer.echo(output)


@app.command()
def load(
    in_file: Path = typer.Argument(None),
    format: services.FileFormat = services.FileFormat.csv,
    dry_run: bool = typer.Option(False, "--dry-run"),
    root_dir: Optional[Path] = typer.Option(None),
):
    if not dry_run:
        kb = KB(root_dir=root_dir)
    else:
        kb = services.PreviewKB(length=10)

    it = services.iterate_entities(in_file=in_file, format=format)
    total = 0
    with typer.progressbar(it) as progress:
        for entity in progress:
            kb.save_entity(entity)
            total += 1

    kb.commit()


@app.command()
def rpc():
    launch_rpc()


@app.command()
def http():
    launch_http()


if __name__ == "__main__":
    app()
