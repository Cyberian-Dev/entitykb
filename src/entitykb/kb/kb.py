from typing import Optional, Union, Dict

from entitykb import (
    __version__,
    Config,
    Edge,
    Node,
    ParseRequest,
    Pipeline,
    Registry,
    SearchRequest,
    SearchResponse,
    under_limit,
    interfaces,
)


class KB(interfaces.IKnowledgeBase):
    config: Config
    pipelines: Dict[str, Pipeline]

    def __init__(self, root=None):
        self.config = Config.create(root=root)

        self.normalizer = self.config.create_normalizer()

        self.tokenizer = self.config.create_tokenizer()

        self.graph = self.config.create_graph(normalizer=self.normalizer)

        self.pipelines = {}
        for name, pipeline_config in self.config.pipelines.items():
            pipeline = pipeline_config.create_pipeline(self)
            self.pipelines[name] = pipeline

    # common

    def __bool__(self):
        return True

    def __len__(self):
        return len(self.graph)

    def __iter__(self):
        yield from self.graph

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
        node = Node.create(node)
        self.graph.save_node(node)
        return node

    def remove_node(self, node_key: Union[Node, str]) -> Node:
        node = self.graph.remove_node(node_key)
        return node

    # edges

    def save_edge(self, edge: Union[Edge, dict]):
        return self.graph.save_edge(edge)

    def connect(self, *, start: Node, verb: str, end: Node):
        return self.graph.connect(start=start, verb=verb, end=end)

    # pipeline

    def parse(self, request: Union[str, ParseRequest]):
        if isinstance(request, str):
            request = ParseRequest(text=request)

        pipeline = self.pipelines.get(request.pipeline)
        assert pipeline, f"Could not find pipeline: {request.pipeline}"
        doc = pipeline(text=request.text, labels=request.labels)
        return doc

    # graph

    def search(self, request: Union[str, SearchRequest]) -> SearchResponse:
        if isinstance(request, str):
            request = SearchRequest(q=request)

        searcher = self._create_searcher(request)
        nodes, trails = self._get_page(request, searcher)
        return SearchResponse.construct(nodes=nodes, trails=trails)

    # admin

    def reload(self):
        self.graph.reload()

    def reindex(self):
        self.graph.reindex()

    def clear(self):
        self.graph.clear()

    def clean_edges(self):
        self.graph.clean_edges()

    def info(self) -> dict:
        return {
            "entitykb": dict(version=__version__),
            "config": self.config.info(),
            "graph": self.graph.info(),
        }

    def get_schema(self) -> dict:
        verbs = sorted(self.graph.get_verbs())
        labels = sorted(self.graph.get_labels())
        schema = Registry.instance().create_schema(labels, verbs)
        return schema.dict()

    # private methods

    def _get_starts(self, request: SearchRequest):
        return self.graph.iterate_keys(
            prefixes=request.q, labels=request.labels, keys=request.keys
        )

    def _create_searcher(self, request: SearchRequest):
        return self.config.create_searcher(
            graph=self.graph,
            traversal=request.traversal,
            starts=self._get_starts(request),
        )

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
