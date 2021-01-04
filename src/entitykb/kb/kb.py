from contextlib import contextmanager
from typing import Optional, Union, Dict, List

from entitykb import (
    __version__,
    Config,
    Direction,
    Doc,
    Entity,
    Edge,
    Node,
    NodeKey,
    Pipeline,
    Registry,
    SearchResponse,
    Traversal,
    User,
    interfaces,
    istr,
)


class KB(interfaces.IKnowledgeBase):
    config: Config
    pipelines: Dict[str, Pipeline]

    def __init__(self, root=None):
        self.config = Config.create(root=root)

        self.user_store = self.config.create_user_store()

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

    def remove_node(self, node_key: NodeKey) -> Node:
        node = self.graph.remove_node(node_key)
        return node

    def get_neighbors(
        self,
        node_key: NodeKey,
        verb: str = None,
        label: str = None,
        direction: Optional[Direction] = None,
        limit: int = 100,
    ) -> List[Node]:

        node_key = Node.to_key(node_key)
        seen_keys = set()
        neighbors = []

        for other_key, _ in self.graph.iterate_edges(
            nodes=node_key, verbs=verb, directions=direction
        ):
            if other_key not in seen_keys:
                seen_keys.add(other_key)
                other_node = self.get_node(other_key)
                if other_node and (label is None or other_node.label == label):
                    neighbors.append(other_node)
                    if len(neighbors) >= limit:
                        break

        return neighbors

    def get_edges(
        self,
        node_key: NodeKey,
        verb: str = None,
        direction: Optional[Direction] = None,
        limit: int = 100,
    ) -> List[Edge]:

        node_key = Node.to_key(node_key)
        edges = []

        for _, edge in self.graph.iterate_edges(
            nodes=node_key, verbs=verb, directions=direction
        ):
            edges.append(edge)
            if len(edges) >= limit:
                break

        return edges

    # edges

    def save_edge(self, edge: Union[Edge, dict]):
        edge = Edge.create(edge)
        return self.graph.save_edge(edge)

    def connect(self, *, start: Node, verb: str, end: Node, data: dict = None):
        return self.graph.connect(start=start, verb=verb, end=end, data=data)

    # pipeline

    def parse(
        self, text: str, labels: istr = None, pipeline: str = "default"
    ) -> Doc:
        pipeline = self.pipelines.get(pipeline)
        assert pipeline, f"Could not find pipeline: {pipeline}"
        doc = pipeline(text=text, labels=labels)
        return doc

    def find(
        self, text: str, labels: istr = None, pipeline: str = "default"
    ) -> List[Entity]:
        doc = self.parse(text=text, labels=labels, pipeline=pipeline)
        return [span.entity for span in doc.spans]

    def find_one(
        self, text: str, labels: istr = None, pipeline: str = "default"
    ) -> Optional[Entity]:
        entities = self.find(text=text, labels=labels, pipeline=pipeline)
        return entities[0] if len(entities) == 1 else None

    # graph

    def search(
        self,
        q: str = None,
        labels: istr = None,
        keys: istr = None,
        traversal: Traversal = None,
        limit: int = 100,
        offset: int = 0,
    ) -> SearchResponse:

        starts = self.graph.iterate_keys(prefixes=q, labels=labels, keys=keys)

        searcher = self.config.create_searcher(
            graph=self.graph, traversal=traversal, starts=starts
        )

        nodes, trails = self.do_search(searcher, limit, offset)

        return SearchResponse.construct(nodes=nodes, trails=trails)

    # admin

    @contextmanager
    def transact(self):
        with self.graph.transact():
            yield

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

    # users

    def authenticate(self, username: str, password: str) -> Optional[str]:
        """ Check username password combo, return user's uuid if valid. """
        return self.user_store.authenticate(
            username=username, password=password
        )

    def get_user(self, token: str) -> Optional[User]:
        """ Return user for valid token from authenticate. """
        return self.user_store.get_user(token)

    # search methods

    def do_search(self, searcher, limit, offset, current=0):
        trail_it = iter(searcher)

        # skip to offset
        to_skip = offset - current
        self.collect(trail_it=trail_it, count=to_skip)

        # collect nodes and trails
        nodes, trails = self.collect(trail_it=trail_it, count=limit)

        return nodes, trails

    def collect(self, trail_it, count):
        trails = []
        nodes = []
        num = 0

        while num < count:
            try:
                trail = next(trail_it)
            except StopIteration:
                break

            node = self.get_node(trail.end)
            if node:
                trails.append(trail)
                nodes.append(node)
                num += 1
                if num >= count:
                    break

        return nodes, trails
