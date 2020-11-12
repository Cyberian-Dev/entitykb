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
    under_limit,
    label_filter,
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

        key = Node.to_key(node)
        previous = self.get_node(key)

        self.graph.save_node(node)

        if isinstance(node, Entity):
            if previous:
                self.terms.remove_entity(previous)
            self.terms.add_entity(node)

        return node

    def remove_node(self, key) -> bool:
        key = Node.to_key(key)
        node = self.graph.remove_node(key)
        if isinstance(node, Entity):
            self.terms.remove_entity(node)
        return node

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
        searcher = self._create_searcher(request)
        nodes, trails = self._get_page(request, searcher)
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

    def get_schema(self) -> dict:
        verbs = self.graph.get_verbs()
        labels = self.graph.get_labels()
        schema = Registry.instance().create_schema(labels, verbs)
        return schema.dict()

    # private methods

    def _get_starts(self, request: SearchRequest):
        if request.q:
            keys = self.terms.iterate_prefix_keys(prefix=request.q)
            starts = filter(label_filter(request.labels), keys)

        else:
            starts = self.graph.iterate_keys(request.keys, request.labels)

        return starts

    def _create_searcher(self, request: SearchRequest):
        starts = self._get_starts(request)
        searcher = Searcher.create(
            self.config.searcher,
            graph=self.graph,
            traversal=request.traversal,
            starts=starts,
        )
        return searcher

    def _get_page(self, request, searcher):
        # paginate request
        # performance tuning opportunity
        # store search with request as key
        # refactor to keep last item for "has_more" logic
        index = -1
        trails = []
        nodes = []

        for trail in searcher:
            index += 1

            if index < request.offset:
                continue

            if under_limit(items=trails, limit=request.limit):
                node = self.get_node(trail.end)
                if node:
                    trails.append(trail)
                    nodes.append(node)
                else:
                    index -= 1
            else:
                break

        return nodes, trails
