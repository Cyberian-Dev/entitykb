from typing import Optional
from entitykb import Node, ParseRequest, Doc, SearchRequest, SearchResponse
from abc import abstractmethod


class BaseKB(object):
    """
    Abstract class that describes all of the public interfaces of KB.
    """

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
    def commit(self) -> bool:
        """ Commit KB to disk. """

    @abstractmethod
    def clear(self) -> bool:
        """ Clear KB of all data. """

    @abstractmethod
    def reload(self) -> bool:
        """ Reload KB from disk. """

    @abstractmethod
    def info(self) -> dict:
        """ Return KB's state and meta info. """

    @abstractmethod
    def get_schema(self) -> dict:
        """ Return schema of nodes and edges. """
