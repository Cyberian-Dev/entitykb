from typing import Optional
from entitykb import Doc, Node
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

    # queries

    @abstractmethod
    def suggest(self, term, query=None):
        """ Suggest term auto-completes, filtered by query. """

    @abstractmethod
    def parse(self, text, labels=None) -> Doc:
        """ Parse text into Doc with entities, filtered by query. """

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
