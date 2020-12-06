from threading import Lock
from collections import defaultdict
from typing import Dict, Set, List

from entitykb.models import Node

lock = Lock()


class NodeIndex(object):
    def __init__(self):
        self.nodes_by_key: Dict[str, Node] = {}
        self.nodes_by_label: Dict[str, List[Node]] = defaultdict(list)

    def __len__(self):
        return len(self.nodes_by_key)

    def __iter__(self):
        return iter(self.nodes_by_key.values())

    def __contains__(self, key):
        return key in self.nodes_by_key

    def get(self, key: str):
        return self.nodes_by_key.get(key)

    def save(self, node: Node):
        with lock:
            if node.key not in self.nodes_by_key:
                self.nodes_by_key[node.key] = node
                self.nodes_by_label[node.label].append(node)

    def remove(self, key: str) -> Node:
        with lock:
            node = self.nodes_by_key.pop(key, None)
            if node:
                nodes = self.nodes_by_label[node.label]
                nodes = [n for n in nodes if n.key != node.key]
                if not nodes:
                    del self.nodes_by_label[node.label]
                else:
                    self.nodes_by_label[node] = nodes
        return node

    def get_labels(self) -> Set[str]:
        return set(self.nodes_by_label.keys())

    def iterate_keys_by_label(self, label):
        nodes = self.nodes_by_label.get(label, [])
        for node in nodes:
            yield node.key
