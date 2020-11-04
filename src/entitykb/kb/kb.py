from importlib import import_module
from typing import Optional, Union

from entitykb import (
    BaseKB,
    Config,
    Edge,
    Entity,
    Graph,
    Node,
    Normalizer,
    ParseRequest,
    Pipeline,
    Registry,
    SearchRequest,
    Searcher,
    SearchResponse,
    Storage,
    TermsIndex,
)


class KB(BaseKB):
    def __init__(self, root: str = None):
        self.uncommitted = 0

        self.config = Config.create(root=root)

        self.storage = Storage.create(
            self.config.storage, root=self.config.root
        )

        self.normalizer = Normalizer.create(self.config.normalizer)

        self.terms = TermsIndex.create(
            self.config.terms, normalizer=self.normalizer
        )

        self.graph = Graph.create(self.config.graph)

        self.searcher = Searcher.create(self.config.searcher, graph=self.graph)

        self.pipelines = {}
        for name, pipeline in self.config.pipelines.items():
            pipeline = Pipeline.create(
                kb=self,
                config=self.config,
                pipeline=pipeline,
                normalizer=self.normalizer,
            )
            self.pipelines[name] = pipeline

        self.modules = [import_module(m) for m in self.config.modules]

        self.reload()

    # common

    def __bool__(self):
        return True

    def __len__(self):
        return len(self.graph)

    def save(self, item):
        if isinstance(item, Node):
            return self.save_node(item)
        elif isinstance(item, Edge):
            return self.save_edge(item)
        else:
            raise RuntimeError(f"Unknown item type: {type(item)}")

    # nodes

    def get_node(self, key: str) -> Optional[Node]:
        return self.graph.get_node(key)

    def save_node(self, node: Union[Node, dict]) -> Node:
        node = Registry.instance().create(Node, node)

        self.graph.save_node(node)

        if isinstance(node, Entity):
            self.terms.add_entity(node)

        return node

    def remove_node(self, key) -> bool:
        return self.graph.remove_node(key)

    # edges

    def save_edge(self, edge):
        return self.graph.save_edge(edge)

    # pipeline

    def parse(self, request: Union[str, ParseRequest]):
        if isinstance(request, str):
            request = ParseRequest(text=request)
        pipeline = self.pipelines.get(request.pipeline)
        assert pipeline, f"Could not find pipeline: {request.pipeline}"
        doc = pipeline(text=request.text, labels=request.labels)
        return doc

    # graph

    def search(self, request: SearchRequest) -> SearchResponse:
        starts = self._get_starts(request)
        trails = self.searcher.search(request.query, starts)
        nodes = [self.get_node(t.end) for t in trails]
        return SearchResponse(nodes=nodes, trails=trails)

    # admin

    def commit(self):
        self.storage.archive()
        py_data = self.terms.get_data(), self.graph.get_data()
        self.storage.save(py_data)
        return True

    def clear(self):
        self.terms.clear_data()
        self.graph.clear_data()
        return True

    def reload(self):
        py_data = self.storage.load()
        if py_data:
            terms_core, graph_core = py_data
            self.terms.put_data(terms_core)
            self.graph.put_data(graph_core)
        return True

    def info(self) -> dict:
        return {
            "config": self.config.info(),
            "storage": self.storage.info(),
            "graph": self.graph.info(),
            "terms": self.terms.info(),
        }

    @classmethod
    def get_schema(cls) -> dict:
        return Registry.instance().schema.dict()

    # private methods

    def _get_starts(self, request):
        starts = []
        if not request.q:
            starts = self.graph

        elif request.input is None or request.input.is_prefix:
            starts = self.terms.iterate_prefix_keys(prefix=request.q)

        elif request.input.is_term:
            starts = self.terms.iterate_term_keys(term=request.q)

        elif request.input.is_key:
            starts = self.graph.iterate_keys(keys=request.q)

        return starts
