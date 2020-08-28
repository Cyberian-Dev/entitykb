from entitykb import logger, Config, LabelSet
from entitykb.pipeline import Pipeline
from .base import BaseKB


class KB(BaseKB):
    def __init__(self, root_dir: str = None):
        self.config = Config.create(root_dir=root_dir)
        self.pipeline = Pipeline.create(config=self.config)
        self.uncommitted = 0

    @property
    def index(self):
        return self.pipeline.index

    @property
    def graph(self):
        return self.index.graph

    # common base interface

    def parse(self, text, *labels):
        """ Parse text string and return Doc with tokens and entities. """
        label_set = LabelSet.create(labels)
        doc = self.pipeline(text=text, label_set=label_set)
        return doc

    def search(self, query):
        """ Search index's terms and graph using the query. """

    def suggest(self, query):
        """ Provide terms based on prefix query for auto-complete. """

    def commit(self):
        """ Commit index's terms and graph to disk. """
        if self.uncommitted:
            self.index.commit()
            logger.warn(f"Committed {self.uncommitted} records.")
            self.uncommitted = 0
        else:
            logger.warn("Nothing to commit.")

    def reset(self):
        """ Clear index's terms and graph of all data. """

    def reload(self):
        """ Reload index's terms and graph data to last commit. """

    def info(self):
        """ Return configuration and metrics information about KB. """
        return {
            "config": self.config.info(),
            "index": self.index.info(),
            "graph": self.graph.info(),
        }

    def save_entity(self, entity):
        """ Save entity by indexing terms and storing in graph. """
        self.index.add_entity(entity=entity)
        self.uncommitted += 1

    def get_entity(self, key_or_id):
        """ Get entity object using it's key or system unique id. """

    def delete_entity(self, key_or_id):
        """ Remove entity object and relationships using it's key or id. """

    def save_resource(self, resource):
        """ Save resources by storing in graph. """

    def get_resource(self, key_or_id):
        """ Get resource object using it's key or system unique id. """

    def delete_resource(self, key_or_id):
        """ Remove resource object and relationships using it's key or id. """

    def save_relationship(self, relationship):
        """ Connect node a to node b with relationship tag. """

    def delete_relationship(self, relationship):
        """ Remove an existing relationship using keys' key/id and tag. """
