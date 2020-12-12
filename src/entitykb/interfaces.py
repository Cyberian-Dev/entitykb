from abc import abstractmethod
from pathlib import Path
from typing import Set, List, Iterable, Optional, Iterator, Tuple, Union

from entitykb import (
    Token,
    Edge,
    Node,
    Entity,
    ParseRequest,
    Span,
    Doc,
    SearchRequest,
    SearchResponse,
    istr,
)

ALL_LABELS = object()


class INormalizer(object):
    def __call__(self, text: str):
        return self.normalize(text)

    @abstractmethod
    def normalize(self, text: str) -> str:
        """ Normalize text and return value. """


class ITokenizer(object):
    def __call__(self, text: str) -> Iterator[Token]:
        return self.tokenize(text)

    def tokenize(self, text) -> Iterator[Token]:
        raise NotImplementedError

    def detokenize(self, tokens: Iterable[Token]) -> str:
        raise NotImplementedError

    def as_tuples(self, text):
        tuples = tuple((str(t), t.ws_after) for t in self(text))
        return tuples


class IGraph(object):
    def __init__(self, root: Path, normalizer: INormalizer):
        self.root = root
        self.normalizer = normalizer

    @abstractmethod
    def __len__(self) -> int:
        """ Return number of nodes in Graph. """

    @abstractmethod
    def __iter__(self) -> Iterable[Node]:
        """ Return iterator of all nodes in the graph. """

    # nodes

    @abstractmethod
    def save_node(self, node: Node):
        """ Save a node to the graph. """

    @abstractmethod
    def get_node(self, key: str) -> Node:
        """ Get a node using key. """

    @abstractmethod
    def remove_node(self, node_key: Union[Node, str]) -> Node:
        """ Remove a node using the node or key. """

    @abstractmethod
    def get_labels(self) -> Set[str]:
        """ Get all labels in graph. """

    # edges

    @abstractmethod
    def save_edge(self, edge: Edge) -> Edge:
        """ Save an edge directly to graph. """

    @abstractmethod
    def remove_edge(self, edge: Edge) -> Edge:
        """ Remove an edge from the graph. """

    @abstractmethod
    def connect(self, *, start: Node, verb: str, end: Node) -> Edge:
        """ Connect 2 nodes with a verb and return the new Edge. """

    @abstractmethod
    def get_verbs(self) -> Set[str]:
        """ Get all the verbs in graph. """

    # iterate

    @abstractmethod
    def iterate_edges(
        self, verbs=None, directions=None, nodes=None
    ) -> Iterable[Edge]:
        """ Iterate all edges based on verbs, directions and nodes. """

    @abstractmethod
    def iterate_keys(
        self,
        keys: istr = None,
        terms: istr = None,
        prefixes: istr = None,
        labels: istr = None,
    ) -> Iterable[str]:
        """ Iterate all keys based on keys and labels. """

    # admin

    @abstractmethod
    def reindex(self):
        """ Run index process on graph to rebuild edges, terms, etc. """

    @abstractmethod
    def reload(self):
        """ Reload indices from disk.  """

    @abstractmethod
    def clear(self):
        """ Clear the graph of all nodes, edges, and terms. """

    @abstractmethod
    def info(self):
        """ Return dictionary of information for the graph. """

    @abstractmethod
    def clean_edges(self):
        """ Removes edges for nodes that no longer exist. """


class IFilterer(object):
    @classmethod
    @abstractmethod
    def filter(cls, spans, tokens) -> List[Span]:
        """ Filter spans based on this filterer's purpose. """


class IKnowledgeBase(object):
    """
    Abstract class that describes all of the public interfaces of KB.
    """

    normalizer: INormalizer
    tokenizer: ITokenizer
    graph: IGraph

    @abstractmethod
    def __len__(self):
        """ Return number of nodes in KB. """

    # nodes

    @abstractmethod
    def get_node(self, key: str) -> Optional[Node]:
        """ Retrieve node using key from KB. """

    @abstractmethod
    def save_node(self, node: Node) -> Node:
        """ Save node to KB. """

    @abstractmethod
    def remove_node(self, key) -> bool:
        """ Remove node and relationships from KB. """

    # edges

    @abstractmethod
    def save_edge(self, edge):
        """ Save edge to KB. """

    # pipeline

    @abstractmethod
    def parse(self, request: ParseRequest) -> Doc:
        """ Parse text into Doc into tokens and spans of entities. """

    # graph

    @abstractmethod
    def search(self, request: SearchRequest) -> SearchResponse:
        """ Suggest term auto-completes, filtered by query. """

    # admin

    @abstractmethod
    def reindex(self):
        """ Reindex node and edge indexes.  """

    @abstractmethod
    def clear(self):
        """ Clear KB of all data. """

    @abstractmethod
    def info(self) -> dict:
        """ Return KB's state and meta info. """

    @abstractmethod
    def get_schema(self) -> dict:
        """ Return schema of nodes and edges. """


class IResolver(object):

    allowed_labels: Set[str] = ALL_LABELS

    def __init__(self, kb: IKnowledgeBase = None):
        self.kb = kb

    def __repr__(self):
        return self.__class__.__name__

    @classmethod
    def get_handler_class(cls):
        pass

    @classmethod
    def is_relevant(cls, labels: Iterable[str]):
        if not bool(labels):
            return True

        if cls.allowed_labels == ALL_LABELS:
            return True

        items = set(labels).intersection(cls.allowed_labels)
        return bool(items)

    @abstractmethod
    def resolve(self, term: str) -> List[Entity]:
        """ Resolve a term into a list of Entity. """

    @abstractmethod
    def is_prefix(self, term: str) -> bool:
        """ Determine if a term is a prefix for a potential entity. """


class IExtractor(object):
    def __init__(
        self, tokenizer: ITokenizer, resolvers: Tuple[IResolver, ...],
    ):
        self.tokenizer = tokenizer
        self.resolvers = resolvers

    def __call__(self, text: str, labels: istr = None) -> Doc:
        return self.extract_doc(text, labels)

    def __repr__(self):
        return self.__class__.__name__

    def extract_doc(self, text: str, labels: istr = None) -> Doc:
        raise NotImplementedError
