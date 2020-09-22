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
    def get_node(self, key: str):
        """ Retrieve node using key from KB. """

    @abstractmethod
    def save_node(self, node):
        """ Save node to KB. """

    @abstractmethod
    def remove_node(self, key):
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
    def parse(self, text, labels=None):
        """ Parse text into Doc with entities, filtered by query. """

    # state

    @abstractmethod
    def commit(self):
        """ Commit KB to disk. """

    @abstractmethod
    def reset(self):
        """ Clear KB of all data. """

    @abstractmethod
    def reload(self):
        """ Reload KB from disk. """

    @abstractmethod
    def info(self):
        """ Return KB's state and meta info. """
