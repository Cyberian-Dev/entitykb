from abc import abstractmethod


class BaseKB(object):
    """
    Abstract class that describes all of the public interfaces of KB.
    """

    @abstractmethod
    def parse(self, text, *labels):
        """ Parse text string and return Doc with tokens and entities. """

    @abstractmethod
    def search(self, query):
        """ Search index's terms and graph using the query. """

    @abstractmethod
    def suggest(self, query):
        """ Provide terms based on prefix query for auto-complete. """

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
    def info(self):
        """ Return configuration and metrics information about KB. """

    @abstractmethod
    def save_entity(self, entity):
        """ Save entity by indexing terms and storing in graph. """

    @abstractmethod
    def get_entity(self, key_or_id):
        """ Get entity object using it's key or system unique id. """

    @abstractmethod
    def delete_entity(self, key_or_id):
        """ Remove entity object and relationships using it's key or id. """

    @abstractmethod
    def save_resource(self, resource):
        """ Save resources by storing in graph. """

    @abstractmethod
    def get_resource(self, key_or_id):
        """ Get resource object using it's key or system unique id. """

    @abstractmethod
    def delete_resource(self, key_or_id):
        """ Remove resource object and relationships using it's key or id. """

    @abstractmethod
    def save_relationship(self, relationship):
        """ Connect node a to node b with relationship tag. """

    @abstractmethod
    def delete_relationship(self, relationship):
        """ Remove an existing relationship using keys' key/id and tag. """
