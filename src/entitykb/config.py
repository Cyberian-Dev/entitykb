from importlib import import_module
import json
import os
from pathlib import Path
from typing import List, Dict

from pydantic import BaseModel, Field

from .logging import logger
from .env import environ
from .models.registry import Registry


class PipelineConfig(BaseModel):
    extractor: str = "entitykb.DefaultExtractor"
    resolvers: List[str] = Field(default=["entitykb.TermResolver"])
    filterers: List[str] = Field(default_factory=list)

    @classmethod
    def default_factory(cls):
        return dict(default=PipelineConfig())


class Config(BaseModel):
    file_path: Path = None

    graph: str = "entitykb.InMemoryGraph"
    modules: List[str] = Field(default_factory=list)
    normalizer: str = "entitykb.LatinLowercaseNormalizer"
    searcher: str = "entitykb.DefaultSearcher"
    storage: str = "entitykb.PickleStorage"
    terms: str = "entitykb.TrieTermsIndex"
    tokenizer: str = "entitykb.WhitespaceTokenizer"

    pipelines: Dict[str, PipelineConfig] = Field(
        default_factory=PipelineConfig.default_factory
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        modules = [import_module(m).__name__ for m in self.modules]
        logger.debug(f"Loading modules: {modules}")
        Registry.reset()

    def __str__(self):
        return f"<Config: {self.file_path}>"

    @property
    def root(self):
        return Path(self.file_path).parent

    @classmethod
    def create(cls, root=None) -> "Config":
        config_file_path = cls.get_file_path(root=root)

        data = {}
        if config_file_path.is_file():
            with open(config_file_path, "r") as fp:
                data = json.load(fp)

        config = cls.make(file_path=config_file_path, data=data)

        if not config_file_path.is_file():
            os.makedirs(os.path.dirname(config_file_path), exist_ok=True)
            with open(config_file_path, "w") as fp:
                json.dump(config.dict(), fp, indent=4)
                fp.write("\n")

        return config

    @classmethod
    def make(cls, file_path: str, data: dict) -> "Config":
        config = Config(file_path=file_path, **data)
        return config

    def dict(self, **kwargs) -> dict:
        data = super(Config, self).dict()
        data.pop("file_path", None)
        return data

    @classmethod
    def get_file_path(cls, root=None, file_name="config.json") -> Path:
        root = cls.get_root(root)
        return root / file_name

    @classmethod
    def get_root(cls, root=None) -> Path:
        return Path(root or environ.root)

    def info(self) -> dict:
        info = self.dict()
        info["root"] = self.root
        return info
