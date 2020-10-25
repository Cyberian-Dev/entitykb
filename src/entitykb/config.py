"""
This module contains Environ class from the Starlette project.


Original Code:

BSD License:
    https://github.com/encode/starlette/blob/master/LICENSE.md
"""

import json
import os
from dataclasses import dataclass, fields
from pathlib import Path
from typing import List
from .deps import CheckEnviron


class Environ(CheckEnviron):
    class DEFAULTS:
        ROOT = os.path.expanduser("~/.entitykb")
        RPC_HOST = "localhost"
        RPC_PORT = 3477
        RPC_TIMEOUT = 2
        RPC_RETRIES = 5
        MV_SPLIT = "|"

    @property
    def root(self) -> str:
        return self.get("ENTITYKB_ROOT", self.DEFAULTS.ROOT)

    @root.setter
    def root(self, value: str):
        self["ENTITYKB_ROOT"] = value

    @property
    def rpc_host(self) -> str:
        return self.get("ENTITYKB_RPC_HOST", self.DEFAULTS.RPC_HOST)

    @rpc_host.setter
    def rpc_host(self, value: str):
        self["ENTITYKB_RPC_HOST"] = value

    @property
    def rpc_port(self) -> int:
        return int(self.get("ENTITYKB_RPC_PORT", self.DEFAULTS.RPC_PORT))

    @rpc_port.setter
    def rpc_port(self, value: int):
        self["ENTITYKB_RPC_PORT"] = str(value)

    @property
    def rpc_timeout(self) -> int:
        return int(self.get("ENTITYKB_RPC_TIMEOUT", self.DEFAULTS.RPC_TIMEOUT))

    @rpc_timeout.setter
    def rpc_timeout(self, value: int):
        self["ENTITYKB_RPC_TIMEOUT"] = str(value)

    @property
    def rpc_retries(self) -> int:
        return int(self.get("ENTITYKB_RPC_RETRIES", self.DEFAULTS.RPC_RETRIES))

    @rpc_retries.setter
    def rpc_retries(self, value: int):
        self["ENTITYKB_RPC_RETRIES"] = str(value)

    @property
    def mv_split(self) -> str:
        return self.get("ENTITYKB_MV_SPLIT", self.DEFAULTS.MV_SPLIT)

    @mv_split.setter
    def mv_split(self, value: str):
        self["ENTITYKB_MV_SPLIT"] = value


environ = Environ()


@dataclass
class Config:
    file_path: str = None
    extractor: str = "entitykb.DefaultExtractor"
    filterers: List[str] = ()
    normalizer: str = "entitykb.LatinLowercaseNormalizer"
    resolvers: List[str] = ("entitykb.TermResolver",)
    tokenizer: str = "entitykb.WhitespaceTokenizer"
    terms: str = "entitykb.TermsIndex"
    graph: str = "entitykb.InMemoryGraph"

    def __str__(self):
        return f"<Config: {self.file_path}>"

    @property
    def root(self):
        return os.path.dirname(self.file_path)

    @classmethod
    def create(cls, root: str) -> "Config":
        config_file_path = cls.get_file_path(root=root)

        data = {}
        if os.path.isfile(config_file_path):
            with open(config_file_path, "r") as fp:
                data = json.load(fp)

        config = cls.construct(file_path=config_file_path, data=data)

        if not os.path.isfile(config_file_path):
            with open(config_file_path, "w") as fp:
                json.dump(config.dict(), fp, indent=4)

        return config

    @classmethod
    def construct(cls, *, file_path: str, data: dict) -> "Config":
        field_names = {class_field.name for class_field in fields(cls)}
        data = {k: v for k, v in data.items() if k in field_names}
        config = Config(file_path=file_path, **data)
        return config

    def dict(self) -> dict:
        kw = {
            "extractor": self.extractor,
            "filterers": self.filterers,
            "normalizer": self.normalizer,
            "resolvers": self.resolvers,
            "terms": self.terms,
            "graph": self.graph,
        }

        return dict((k, v) for k, v in kw.items())

    @classmethod
    def get_file_path(cls, root=None, file_name="config.json"):
        root = cls.get_root(root)
        file_path = os.path.join(root, file_name)
        return file_path

    @classmethod
    def get_root(cls, root=None) -> str:
        if isinstance(root, Path):
            root = str(root.resolve())

        root = root or environ.root

        return root

    def info(self) -> dict:
        info = self.dict()
        info["root"] = self.root
        info["resolvers"] = self.resolvers
        info["filterers"] = self.filterers
        return info
