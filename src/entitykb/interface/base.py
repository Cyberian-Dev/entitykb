from abc import abstractmethod


class BaseKB(object):
    @abstractmethod
    def parse(self, text, *labels):
        """ Parse text string and return Doc with tokens and entities. """

    @abstractmethod
    def save_entity(self, entity):
        """ Save entity by indexing terms and storing in graph. """

    @abstractmethod
    def get_entity(self, key_or_id):
        """ Get entity object using it's key or system unique id. """

    @abstractmethod
    def save_resource(self, resource):
        """ Save resources by storing in graph. """

    @abstractmethod
    def get_resource(self, key_or_id):
        """ Get resource object using it's key or system unique id. """

    @abstractmethod
    def save_relationship(self, a, tag, b):
        """ Connect node a to node b with relationship tag. """

    @abstractmethod
    def commit(self):
        """ Commit index's terms and graph to disk. """

    @abstractmethod
    def reset(self):
        """ Clear index's terms and graph of all data. """

    @abstractmethod
    def reload(self):
        """ Reload index's terms and graph data to last commit. """

    @abstractmethod
    def search(self, query):
        """ Search index's terms and graph using the query. """

    @abstractmethod
    def suggest(self, query):
        """ todo: this different from search? prefix-based query => terms """
