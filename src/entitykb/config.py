import json
from importlib import import_module
from pathlib import Path
from typing import Dict, List

from pydantic import BaseModel, Field

from .env import environ
from .logging import logger
from .models.registry import Registry
from .reflection import create_component, get_class_from_name
from .crypto import generate_secret


class PipelineConfig(BaseModel):
    extractor: str = "entitykb.DefaultExtractor"
    resolvers: List[str] = Field(default=["entitykb.TermResolver"])
    filterers: List[str] = Field(default_factory=list)

    @classmethod
    def default_factory(cls):
        return dict(default=PipelineConfig())

    def create_pipeline(self, kb):
        from entitykb.pipeline.pipeline import Pipeline

        resolvers = tuple(
            create_component(value=resolver, kb=kb)
            for resolver in self.resolvers
        )

        extractor = self.create_extractor(
            tokenizer=kb.tokenizer, resolvers=resolvers
        )

        filterers = self.create_filterers()
        return Pipeline(extractor=extractor, filterers=filterers)

    def create_filterers(self):
        return tuple(get_class_from_name(f) for f in self.filterers)

    def create_extractor(self, tokenizer, resolvers):
        from entitykb.pipeline.extractors import DefaultExtractor

        return create_component(
            value=self.extractor,
            default_cls=DefaultExtractor,
            tokenizer=tokenizer,
            resolvers=resolvers,
        )


class Config(BaseModel):
    file_path: Path = None

    graph: str = "entitykb.Graph"
    modules: List[str] = Field(default_factory=list)
    normalizer: str = "entitykb.LatinLowercaseNormalizer"
    searcher: str = "entitykb.DefaultSearcher"
    tokenizer: str = "entitykb.WhitespaceTokenizer"
    user_store: str = "entitykb.UserStore"
    secret_key: str = Field(default_factory=generate_secret)

    pipelines: Dict[str, PipelineConfig] = Field(
        default_factory=PipelineConfig.default_factory
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        modules = [import_module(m).__name__ for m in self.modules]
        logger.debug(f"Loading modules: {modules}")
        Registry.reset()

    def __str__(self):
        return f"<Config: {self.file_path}>"

    @property
    def root(self):
        return Path(self.file_path).parent

    @classmethod
    def create(cls, root=None, config=None) -> "Config":
        config_file_path = cls.get_file_path(root=root)

        data = {}
        if config_file_path.is_file():
            with config_file_path.open("r") as fp:
                data = json.load(fp)

        config = config or cls(file_path=config_file_path, **data)

        if not config_file_path.is_file():
            config_file_path.parent.mkdir(parents=True, exist_ok=True)
            with config_file_path.open(mode="w") as fp:
                json.dump(config.dict(), fp, indent=4)
                fp.write("\n")

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
        info["secret_key"] = self.secret_key[:6] + "..."
        info["root"] = str(self.root)
        return info

    def create_user_store(self):
        from entitykb.user_store import UserStore

        return create_component(
            value=self.user_store,
            default_cls=UserStore,
            root=self.root,
            secret_key=self.secret_key,
        )

    def create_normalizer(self):
        from entitykb.pipeline.normalizers import LatinLowercaseNormalizer

        return create_component(
            value=self.normalizer, default_cls=LatinLowercaseNormalizer
        )

    def create_tokenizer(self):
        from entitykb.pipeline.tokenizers import WhitespaceTokenizer

        return create_component(
            value=self.tokenizer, default_cls=WhitespaceTokenizer
        )

    def create_graph(self, normalizer):
        from entitykb.graph import Graph

        return create_component(
            value=self.graph,
            default_cls=Graph,
            root=self.root,
            normalizer=normalizer,
        )

    def create_searcher(self, graph, starts, traversal):
        from entitykb.searcher import DefaultSearcher

        return create_component(
            value=self.searcher,
            default_cls=DefaultSearcher,
            graph=graph,
            traversal=traversal,
            starts=starts,
        )
