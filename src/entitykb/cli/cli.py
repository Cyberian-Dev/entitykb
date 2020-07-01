import os
import sys
from typing import List

import click
import tabulate
from click.exceptions import Exit

from entitykb import Config, load
from . import etl, render_doc


@click.group()
def cli():
    pass


@cli.command()
@click.argument(
    "root_dir", type=click.Path(), required=False,
)
def init(root_dir: str):
    """ Initialize new entitykb root directory. """
    root_dir = Config.get_root_dir(root_dir)

    if os.path.isfile(root_dir):
        raise Exit(f"KB directory is invalid ({root_dir}")

    if not os.path.isdir(root_dir):
        click.echo(f"Creating KB directory: {root_dir}")
        os.makedirs(root_dir, exist_ok=True)

    file_path = Config.get_file_path(root_dir)
    if os.path.isfile(file_path):
        raise Exit(f"KB config already exists: ({file_path}")

    click.echo(f"Initializing KB: {root_dir}")
    kb = load(root_dir=root_dir)
    kb.commit()
    click.echo("Initialization Complete.")


@cli.command()
@click.argument(
    "root_dir", type=click.Path(), required=False,
)
def reset(root_dir: str):
    """ Reset an entitykb index. """
    kb = load(root_dir=root_dir)
    if not kb.index.exists:
        raise Exit(f"KB index does not exist: {kb.index.index_path}")

    click.confirm(
        f"Are you sure you want to remove: {kb.index.index_path}?", abort=True,
    )

    backup_path = kb.index.backup_index()
    if backup_path:
        click.echo(f"Backed up current index to: {backup_path}")

    cleaned_path = kb.index.clean_backups()
    if cleaned_path:
        click.echo(f"Removed oldest backup: {cleaned_path}")

    kb.index.reset()
    index_path = kb.index.commit()
    click.echo(f"Index reset: {index_path}")


@cli.command()
@click.argument(
    "root_dir", type=click.Path(), required=False,
)
def info(root_dir: str):
    """ Print entitykb stats and meta information. """
    kb = load(root_dir=root_dir)
    data = kb.info()

    flat = {}
    for k0, v0 in data.items():
        if isinstance(v0, dict):
            for k1, v1 in v0.items():
                flat[k0 + "." + k1] = v1
        else:
            flat[k0] = v0

    output = tabulate.tabulate(
        flat.items(), tablefmt="pretty", colalign=("left", "right"),
    )
    click.echo(output)


@cli.command("load")
@click.argument("in_file", type=click.File("r"), default=sys.stdin)
@click.option(
    "--csv",
    "dialect",
    flag_value="excel",
    default=True,
    help="Specify input format is CSV (default).",
)
@click.option(
    "--tsv",
    "dialect",
    flag_value="excel-tab",
    help="Specify input format is TSV.",
)
@click.option(
    "--multi",
    "-m",
    "multi",
    help="Multi-value fields split on by separator.",
    type=str,
    multiple=True,
)
@click.option(
    "--label",
    "-l",
    "label",
    help="Default label if not provided. (default: ENTITY)",
    default="ENTITY",
    type=str,
)
@click.option(
    "--sep",
    "sep",
    default="|",
    help="Separator to split multi-value fields. (default: |)",
    type=str,
)
@click.option(
    "--name",
    "-n",
    "name",
    default=None,
    help="Entity 'name' field. (default: name)",
    type=str,
)
@click.option(
    "--synonyms",
    "-s",
    "synonyms",
    default=None,
    help="Entity 'synonyms' field. (default: synonyms)",
    type=str,
)
@click.option(
    "--key",
    "-k",
    "key_format",
    default="{name}|{label}",
    help="Key identifier formatting. (default: {name}|{label})",
    type=str,
)
@click.option(
    "--ignore",
    "-i",
    multiple=True,
    help="Column names to drop from entity meta information.",
)
@click.option(
    "--dry-run",
    "dry_run",
    is_flag=True,
    help="Display the first 10 entities without loading.",
)
@click.option(
    "--root_dir", "root_dir", help="Root directory of knowledge base."
)
def load_data(
    in_file: str,
    dialect: str,
    multi: List,
    sep: str,
    label: str,
    name: str,
    synonyms: str,
    key_format: str,
    ignore: list,
    dry_run: bool,
    root_dir: str,
):
    """ Load data from CSV/TSV input file or stream. """

    kb = load(root_dir=root_dir)

    count = 0
    it = etl.iterate_entities(
        in_file, dialect, multi, sep, label, name, synonyms, key_format, ignore
    )
    preview = []

    for entity in it:
        if dry_run:
            d = entity.dict()
            d.pop("key", None)
            d.pop("meta", None)
            preview.append(d)
            if count > 10:
                break
        else:
            kb.add(entity)
        count += 1

    if not dry_run:
        kb.commit()
        print(f"Loaded {count} records.")
    else:
        output = tabulate.tabulate(
            preview, headers="keys", tablefmt="pretty", colalign=("left",) * 3,
        )
        click.echo(output)

        click.echo("Dry run complete. Loaded 0 records.")


@cli.command()
@click.argument("in_file", type=click.File("r"), default="-")
@click.option(
    "--root_dir", "root_dir", help="Specify root directory of knowledge base."
)
@click.option("--table", "output_format", flag_value="table", default=True)
@click.option("--json", "output_format", flag_value="json")
@click.option("--jsonl", "output_format", flag_value="jsonl")
@click.option("--csv", "output_format", flag_value="csv")
@click.option("--tsv", "output_format", flag_value="tsv")
def process(in_file, root_dir, output_format):
    """ Process text into a document (JSON) or entity rows (table/JSONL). """

    kb = load(root_dir=root_dir)
    text = in_file.read().strip()

    doc = kb(text)
    doc.entities = sorted(doc.entities, key=lambda de: de.offset)

    click.echo_via_pager(render_doc(doc, output_format),)


def main():
    cli()


if __name__ == "__main__":
    cli()
