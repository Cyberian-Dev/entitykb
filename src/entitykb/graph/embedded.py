from .model import Node, Edge, Direction, ensure_iterable


class Tag(object):
    def __init__(self, tag: str):
        self.tag = tag


class NestedDict(dict):
    def __missing__(self, key):
        value = NestedDict()
        self[key] = value
        return value


class EdgeIndex(object):
    def __init__(self):
        self.by_node_key = NestedDict()
        self.by_edge_tag = NestedDict()

    @classmethod
    def edge_keys(cls, edge: Edge):
        yield edge.start, Direction.outgoing, edge.tag, edge.end
        yield edge.end, Direction.incoming, edge.tag, edge.start

    def save(self, edge):
        for a, dir, tag, b in self.edge_keys(edge):
            self.by_node_key[a][dir][tag][b] = edge
            self.by_edge_tag[tag][dir][a][b] = edge

    def iterate(self, tags=None, directions=None, keys=None):
        tags = (None,) if tags is None else tags
        directions = tuple(Direction) if directions is None else directions
        keys = (None,) if keys is None else keys

        for tag in ensure_iterable(tags):
            for direction in ensure_iterable(directions):
                for key in ensure_iterable(keys):
                    # yield from self._do_iter(tag, direction, key)
                    yield from []


class Graph(object):
    def __init__(self):
        self.nodes = {}
        self.edges = EdgeIndex()

    def save_node(self, node: Node):
        self.nodes[node.key] = node

    def get_node(self, key: str):
        return self.nodes[key]

    def connect(self, *, start: Node, tag: str, end: Node, **meta):
        edge = Edge(start=start, tag=tag, end=end, meta=meta)
        self.save_edge(edge)
        return edge

    def save_edge(self, edge: Edge):
        self.edges.save(edge)
