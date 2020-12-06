from threading import Lock
from collections import defaultdict
from typing import Dict, Set, List

from entitykb.models import Node, SmartList

lock = Lock()


class NodeIndex(object):
    def __init__(self):
        self.nodes_by_key: Dict[str, Node] = {}
        self.keys_by_label: Dict[str, List[str]] = defaultdict(SmartList)

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
            self.nodes_by_key[node.key] = node
            self.keys_by_label[node.label].append(node.key)

    def remove(self, key: str) -> Node:
        with lock:
            node = self.nodes_by_key.pop(key, None)
            if node:
                self.keys_by_label[node.label].remove(node.key)
        return node

    def get_labels(self) -> Set[str]:
        return set(self.keys_by_label.keys())

    def iterate_keys_by_label(self, label):
        yield from self.keys_by_label.get(label, [])
