import collections
import os

import typer

from entitykb import Config, KB, logger


class PreviewKB(object):
    def __init__(self, count=10, echo=None):
        self.dry_run = []
        self.count = count
        self.echo = echo or typer.echo

    def save_node(self, node):
        if self.count > 0:
            self.count -= 1
            self.dry_run.append(node)

    def commit(self):
        for item in self.dry_run:
            self.echo(item)


def init_kb(root, exist_ok=False) -> bool:
    success = False

    try:
        root = Config.get_root(root)

        os.makedirs(str(root), exist_ok=exist_ok)
        Config.create(root=root)

        kb = KB(root=root)
        kb.reindex()
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
