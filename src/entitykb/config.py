import os
from dataclasses import dataclass, field, fields
from typing import List

import ujson

import entitykb


@dataclass
class Config:
    file_path: str = None
    extractor: str = "entitykb.DefaultExtractor"
    filterers: List[str] = field(default_factory=list)
    index: str = "entitykb.DefaultIndex"
    normalizer: str = "entitykb.DefaultNormalizer"
    resolvers: List[str] = None
    tokenizer: str = "entitykb.DefaultTokenizer"

    def __post_init__(self):
        self.resolvers = self.resolvers or ["entitykb.DefaultResolver"]

    def __str__(self):
        return f"<Config: {self.file_path}>"

    @property
    def root_dir(self):
        return os.path.dirname(self.file_path)

    @classmethod
    def create(cls, root_dir: str) -> "Config":
        config_file_path = entitykb.Config.get_file_path(root_dir=root_dir)

        data = {}
        if os.path.isfile(config_file_path):
            with open(config_file_path, "r") as fp:
                data = ujson.load(fp)

        config = cls.construct(file_path=config_file_path, data=data)

        if not os.path.isfile(config_file_path):
            with open(config_file_path, "w") as fp:
                ujson.dump(config.dict(), fp, indent=4)

        return config

    @classmethod
    def construct(cls, *, file_path: str, data: dict) -> "Config":
        field_names = {class_field.name for class_field in fields(cls)}
        data = {k: v for k, v in data.items() if k in field_names}
        config = Config(file_path=file_path, **data)
        return config

    def dict(self) -> dict:
        return {
            "extractor": self.extractor,
            "filterers": self.filterers,
            "index": self.index,
            "normalizer": self.normalizer,
            "resolvers": self.resolvers,
            "tokenizer": self.tokenizer,
        }

    @classmethod
    def get_file_path(cls, root_dir=None, file_name="config.json"):
        root_dir = cls.get_root_dir(root_dir)
        file_path = os.path.join(root_dir, file_name)
        return file_path

    @classmethod
    def get_root_dir(cls, root_dir=None):
        root_dir = (
            root_dir
            or os.environ.get("ENTITYKB_ROOT")
            or os.path.expanduser("~/.entitykb")
        )
        return root_dir

    def info(self) -> dict:
        info = self.dict()
        info["path"] = self.file_path
        info["resolvers"] = "\n".join(self.resolvers)
        info["filterers"] = "\n".join(self.filterers)
        return info
