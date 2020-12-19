from typing import Union, Any, Tuple, Optional
from uuid import uuid4

from pydantic import BaseModel, Field, validator

from .funcs import camel_to_snake
from .enums import TripleSep as TS

label_cache = {}


class Node(BaseModel):
    key: str = Field(default_factory=lambda: str(uuid4()))
    label: str
    data: dict = None

    __all_labels__ = {"NODE"}
    __default_label__ = "NODE"

    class Config:
        allow_mutation = False

    def __init__(self, **data: Any):
        if "label" not in data:
            data["label"] = self.get_default_label()
        super().__init__(**data)

    def __lt__(self, other):
        return self.key < other.key

    def __hash__(self):
        return hash((self.label, self.key))

    def __rshift__(self, verb):
        return Edge(start=self.key, verb=verb, end=None)

    def __lshift__(self, verb):
        return Edge(start=None, verb=verb, end=self.key)

    @property
    def terms(self):
        return ()

    @staticmethod
    def to_key(node_key: Union["Node", str]) -> str:
        try:
            return node_key.key
        except AttributeError:
            return node_key

    @classmethod
    def get_default_label(cls):
        default_label = cls.__dict__.get("__default_label__")
        if default_label is None:
            default_label = label_cache.get(cls.__name__)
            if default_label is None:
                default_label = camel_to_snake(cls.__name__, upper=True)
                label_cache[cls.__name__] = default_label
        return default_label

    @classmethod
    def get_all_labels(cls):
        labels = set(cls.__dict__.get("__all_labels__", ()))
        labels.add(cls.get_default_label())
        return labels

    @classmethod
    def create(cls, *args, **kwargs):
        from .registry import Registry

        registry = Registry.instance()
        return registry.create(cls, *args, **kwargs)


class Edge(BaseModel):
    __root__: Tuple[Optional[str], ...]

    def __init__(self, *, start=None, verb=None, end=None, __root__=None):
        if not __root__:
            from .traverse import Verb

            __root__ = (Node.to_key(start), Verb[verb], Node.to_key(end))

        super().__init__(__root__=__root__)

    def __hash__(self):
        return hash(self.__root__)

    def __eq__(self, other):
        return bool(other and self.__root__ == other)

    def __getitem__(self, item):
        return self.__root__[item]

    def __repr__(self):
        return (
            f"Edge(start='{self.start}', verb='{self.verb}', end='{self.end}')"
        )

    def __rshift__(self, end: Union[Node, str]):
        self.set_end(end)
        return self

    def __lshift__(self, start: Union[Node, str]):
        self.set_start(start)
        return self

    @property
    def key(self):
        return self.sve

    @property
    def start(self):
        return self[0]

    def set_start(self, start):
        start = Node.to_key(start)
        self.__root__ = (start, self.__root__[1], self.__root__[2])

    @property
    def verb(self):
        return self[1]

    def set_verb(self, verb):
        from .traverse import Verb

        self.__root__ = (self.__root__[0], Verb[verb], self.__root__[2])

    @property
    def end(self):
        return self[2]

    def set_end(self, end):
        end = Node.to_key(end)
        self.__root__ = (self.__root__[0], self.__root__[1], end)

    def get_other(self, direction):
        return self.end if direction.is_outgoing else self.start

    @property
    def sve(self):
        return f"{TS.sve}{self.start}{TS.sve}{self.verb}{TS.sve}{self.end}"

    @property
    def vse(self):
        return f"{TS.vse}{self.verb}{TS.vse}{self.start}{TS.vse}{self.end}"

    @property
    def evs(self):
        return f"{TS.evs}{self.end}{TS.evs}{self.verb}{TS.evs}{self.start}"

    @property
    def vbs(self):
        return f"{TS.vbs}{self.verb}"

    @classmethod
    def create(cls, line: str, ts: TS = TS.sve):
        if ts.is_sve:
            _, start, verb, end = line.split(ts)
        elif ts.is_vse:
            _, verb, start, end = line.split(ts)
        else:
            _, end, verb, start = line.split(ts)

        return Edge(__root__=(start, verb, end))
