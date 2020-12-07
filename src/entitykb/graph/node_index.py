from threading import Lock
from typing import Set

from dawg import CompletionDAWG

from entitykb import Node

lock = Lock()


class BaseNodeIndex(object):
    def __len__(self):
        raise NotImplementedError

    def __iter__(self):
        raise NotImplementedError

    def __contains__(self, key):
        raise NotImplementedError

    def commit(self):
        raise NotImplementedError

    def get(self, key: str):
        raise NotImplementedError

    def save(self, node: Node):
        raise NotImplementedError

    def remove(self, key: str) -> Node:
        raise NotImplementedError

    def get_labels(self) -> Set[str]:
        raise NotImplementedError

    def iterate_keys_by_label(self, label):
        raise NotImplementedError


class NodeIndex(BaseNodeIndex):
    key_sep = "\1"
    label_sep = "\2"

    def __init__(self):
        self.dawg = CompletionDAWG([])
        self.labels = set()
        self.adds = {}
        self.removes = set()

    def __len__(self):
        return len(self.dawg.keys(self.key_sep))

    def __iter__(self):
        for item in self.dawg.iterkeys(self.key_sep):
            yield self._to_node(item)

    def __contains__(self, key):
        prefix = self._node_prefix(key)
        return self.dawg.has_keys_with_prefix(prefix)

    def commit(self):
        by_label, data = self._process_add_removes()
        self.dawg = self._make_dawg(by_label, data)
        self.labels = set(by_label.keys())
        self.adds.clear()
        self.removes.clear()

    def get(self, key: str):
        prefix = self._node_prefix(key)
        items = self.dawg.iterkeys(prefix)
        first = None
        second = None

        try:
            first = next(items)
            second = next(items)
        except StopIteration:
            pass

        if first is not None and second is None:
            return self._to_node(first)

    def save(self, node: Node):
        self.adds[node.key] = node
        self.removes.discard(node.key)

    def remove(self, key: str) -> Node:
        current = self.get(key)
        self.removes.add(key)
        self.adds.pop(key, None)
        return current

    def get_labels(self) -> Set[str]:
        return self.labels

    def iterate_keys_by_label(self, label):
        prefix = self._label_prefix(label)
        for item in self.dawg.iterkeys(prefix):
            _, key = item.rsplit(self.label_sep, maxsplit=1)
            yield key

    @classmethod
    def _node_prefix(cls, key: str):
        return f"{cls.key_sep}{key}{cls.key_sep}"

    @classmethod
    def _label_prefix(cls, label: str):
        return f"{cls.label_sep}{label}{cls.label_sep}"

    @classmethod
    def _to_node(cls, item: str):
        _, json = item.rsplit(cls.key_sep, maxsplit=1)
        return Node.deserialize(json=json)

    def _process_add_removes(self):
        data = {}
        by_label = {}
        for key, node in self.adds.items():
            if key not in self.removes:
                data[key] = node.serialize()
                by_label.setdefault(node.label, set()).add(key)
        for item in self.dawg.iterkeys(self.key_sep):
            _, key, json = item.rsplit(self.key_sep, maxsplit=2)
            if key not in self.removes and key not in data:
                data[key] = json
                split = key.rsplit("|", maxsplit=1)
                if len(split) == 2:
                    key, label = split
                else:
                    label = Node.deserialize(json).label
                by_label.setdefault(label, set()).add(key)
        return by_label, data

    def _make_dawg(self, by_label, data):
        combined = []

        for key, json in data.items():
            line = f"{self.key_sep}{key}{self.key_sep}{json}"
            combined.append(line)

        for label, keys in by_label.items():
            for key in keys:
                line = f"{self.label_sep}{label}{self.label_sep}{key}"
                combined.append(line)

        return CompletionDAWG(combined)
