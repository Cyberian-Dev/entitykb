import collections
import os

import typer

from entitykb import Config, KB, logger


def init_kb(root, exist_ok=False, config=None) -> bool:
    success = False

    try:
        root = Config.get_root(root)

        os.makedirs(str(root), exist_ok=exist_ok)
        Config.create(root=root, config=config)

        KB(root=root)
        success = True

    except FileExistsError as e:
        logger.error(e)

    return success


def flatten_dict(d, parent_key="", sep="."):
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, collections.MutableMapping):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        elif isinstance(v, (list, tuple)):
            items.append((new_key, "\n".join(map(str, v))))
        else:
            items.append((new_key, v))
    return dict(items)


def finish(operation: str, success: bool, error_code: int = None):
    if success:
        logger.info(f"{operation} completed successfully.")
    else:
        logger.warning(f"{operation} failed.")
        raise typer.Exit(error_code or 1)
