from abc import abstractmethod
from pathlib import Path
from typing import Iterable, Iterator, List, Optional, Set, Tuple

from entitykb import (
    Direction,
    Doc,
    Edge,
    Entity,
    Node,
    NodeKey,
    SearchResponse,
    Span,
    Token,
    Traversal,
    User,
    istr,
)

ALL_LABELS = object()


class IUserStore(object):
    def __init__(self, root: Path):
        self.root = root

    @abstractmethod
    def authenticate(self, username: str, password: str) -> Optional[str]:
        """ Returns token if username/password match. """

    @abstractmethod
    def get_user(self, token: str) -> Optional[User]:
        """ Return user for valid token from authenticate. """


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
    def remove_node(self, node_key: NodeKey) -> Node:
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
    def remove_edges(self, node: NodeKey) -> Edge:
        """ Remove an edge from the graph. """

    @abstractmethod
    def connect(
        self, *, start: Node, verb: str, end: Node, data: dict = None
    ) -> Edge:
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
        """ Iterate all keys based on keys, terms, prefixes and labels. """

    @abstractmethod
    def iterate_nodes(
        self,
        keys: istr = None,
        terms: istr = None,
        prefixes: istr = None,
        labels: istr = None,
    ) -> Iterable[Node]:
        """ Iterate all nodes based on keys, terms, prefixes and labels. """

    # admin

    @abstractmethod
    def transact(self):
        """ Open up transaction for locking. """

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
    """
    Abstract class that processes spans
    """

    def __init__(self, doc: Doc = None):
        self.doc = doc

    def is_keep(self, span: Span):
        return True

    def filter(self, spans: Iterator[Span]) -> Iterator[Span]:
        return filter(self.is_keep, spans)


class IKnowledgeBase(object):
    """
    Abstract class that describes all of the public interfaces of KB.
    """

    normalizer: INormalizer
    tokenizer: ITokenizer
    graph: IGraph
    user_store: IUserStore

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
    def remove_node(self, key) -> Node:
        """ Remove node and relationships from KB. """

    @abstractmethod
    def get_neighbors(
        self,
        node_key: NodeKey,
        verb: str = None,
        label: str = None,
        direction: Optional[Direction] = None,
    ) -> List[Node]:
        """ Retrieve unique neighbor nodes. """

    @abstractmethod
    def get_edges(
        self,
        node_key: NodeKey,
        verb: str = None,
        direction: Optional[Direction] = None,
    ) -> List[Edge]:
        """ Get edges for a given Node. """

    # edges

    @abstractmethod
    def save_edge(self, edge: Edge):
        """ Save edge to KB. """

    # pipeline

    @abstractmethod
    def parse(
        self, text: str, labels: istr = None, pipeline: str = "default"
    ) -> Doc:
        """ Parse text into Doc into tokens and spans of entities. """

    @abstractmethod
    def find(
        self, text: str, labels: istr = None, pipeline: str = "default"
    ) -> List[Entity]:
        """ Parse text into and return all found entities. """

    @abstractmethod
    def find_one(
        self, text: str, labels: istr = None, pipeline: str = "default"
    ) -> Optional[Entity]:
        """ Parse text into and return entity, if 1 and only 1 found. """

    # graph

    @abstractmethod
    def search(
        self,
        q: str = None,
        labels: istr = None,
        keys: istr = None,
        traversal: Traversal = None,
        limit: int = 100,
        offset: int = 0,
    ) -> SearchResponse:
        """ Suggest term auto-completes, filtered by query. """

    # admin

    @abstractmethod
    def transact(self):
        """ Start transaction for locking for loading. """

    @abstractmethod
    def reload(self):
        """ Reindex node and edge indexes.  """

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

    @abstractmethod
    def authenticate(self, username: str, password: str) -> Optional[str]:
        """ Returns token if username/password match. """

    @abstractmethod
    def get_user(self, token: str) -> Optional[User]:
        """ Return user for valid token from authenticate. """


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
    def is_relevant(cls, labels: istr):
        if not bool(labels):
            return True

        if cls.allowed_labels == ALL_LABELS:
            return True

        items = set(labels).intersection(cls.allowed_labels)
        return bool(items)

    @abstractmethod
    def resolve(self, term: str, labels: istr = None) -> List[Entity]:
        """ Resolve a term into a list of Entity. """

    @abstractmethod
    def is_prefix(self, term: str, labels: istr = None) -> bool:
        """ Determine if a term is a prefix for a potential entity. """


class IExtractor(object):
    def __init__(
        self,
        tokenizer: ITokenizer,
        resolvers: Tuple[IResolver, ...],
    ):
        self.tokenizer = tokenizer
        self.resolvers = resolvers

    def __call__(self, text: str, labels: istr = None) -> Doc:
        return self.extract_doc(text, labels)

    def __repr__(self):
        return self.__class__.__name__

    def extract_doc(self, text: str, labels: istr = None) -> Doc:
        raise NotImplementedError
