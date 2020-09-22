import asyncio

from entitykb import Doc, Node
from .client_async import AsyncKB


def run_future(future):
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(future)
    return result


class SyncKB(AsyncKB):
    """ EntityKB RPC Client """

    def __len__(self):
        pass

    def get_node(self, key: str) -> Node:
        raise NotImplementedError

    def save_node(self, node: Node):
        future = super(SyncKB, self).save_node(node)
        doc = run_future(future)
        return doc

    def remove_node(self, key):
        raise NotImplementedError

    def save_edge(self, edge):
        raise NotImplementedError

    def suggest(self, term, query=None):
        raise NotImplementedError

    def parse(self, text, labels=None) -> Doc:
        future = super(SyncKB, self).parse(text, labels=labels)
        doc = run_future(future)
        return doc

    def commit(self):
        future = super(SyncKB, self).commit()
        count = run_future(future)
        return count

    def reset(self):
        future = super(SyncKB, self).reset()
        success = run_future(future)
        return success

    def reload(self):
        raise NotImplementedError

    def info(self):
        future = super(SyncKB, self).info()
        data = run_future(future)
        return data
