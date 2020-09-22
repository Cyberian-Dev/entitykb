from entitykb import Config, BaseKB, Graph, Entity
from entitykb.pipeline import Pipeline, Normalizer, FindResult
from entitykb.terms import Terms
from .storage import DefaultStorage


class KB(BaseKB):
    def __init__(self, root_dir: str = None):
        self.uncommitted = 0
        self.storage = DefaultStorage(root_dir=root_dir)
        self.config = Config.create(root_dir=root_dir)
        self.normalizer = Normalizer.create(self.config.normalizer)
        self.terms = Terms(normalizer=self.normalizer)
        self.graph = Graph()
        self.pipeline = Pipeline.create(
            kb=self, config=self.config, normalizer=self.normalizer
        )
        self.load()

    # common base interface

    def __len__(self):
        return len(self.graph)

    def is_prefix(self, prefix, labels=None):
        """ Returns True if prefix exists for given labels. """
        if labels:
            term_iter = self.terms.iterate_prefix_keys(prefix)
            for key in term_iter:
                node = self.graph.get_node(key)
                if node.label in labels:
                    return True

            return False
        else:
            return self.terms.is_prefix(prefix=prefix)

    def find(self, term: str = None, labels=None, limit: int = None):
        term_iter = self.terms.iterate_term_keys(term=term)
        entities = []
        for key in term_iter:
            entity = self.graph.get_node(key)
            entities.append(entity)

        # query = QB(term=term)
        # if labels:
        #     query = query.filter(label=labels)
        # query = query.limit(limit)
        #
        # results = self.searcher.search(query)

        return FindResult(term=term, entities=entities)

    def parse(self, text, labels=None):
        """ Parse text string and return Doc with tokens and entities. """
        doc = self.pipeline(text=text, labels=labels)
        return doc

    def search(self, query):
        """ Search index's terms and graph using the query. """

    def suggest(self, query):
        """ Provide terms based on prefix query for auto-complete. """

    def save_entity(self, entity: Entity):
        """ Save entity by indexing terms and storing in graph. """
        self.graph.save_node(entity)
        for term in entity.terms:
            self.terms.add_term(term, entity)
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

    # data

    def info(self) -> dict:
        return {
            "storage": self.storage.info(),
        }

    def load(self):
        py_data = self.storage.load()
        if py_data:
            terms_core, graph_core = py_data
            self.terms.put_data(terms_core)
            self.graph.put_data(graph_core)

    def commit(self):
        self.storage.archive()
        py_data = self.terms.get_data(), self.graph.get_data()
        self.storage.save(py_data)

    def reset(self):
        self.terms.reset_data()
        self.graph.reset_data()

    def reload(self):
        pass
