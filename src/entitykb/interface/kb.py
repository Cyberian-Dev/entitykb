import entitykb
from entitykb.model import Doc, Entity, Node, Resource, Relationship
from .base import BaseKB


class KB(BaseKB):
    def __init__(self, core=None):
        # todo: entitykb.KB is the "core" that houses pipeline, graph, etc.
        # todo: renaming/refactoring and this class becomes "public" KB
        self.core: entitykb.KB = core or entitykb.load()

    def parse(self, text: str, *labels: str) -> Doc:
        doc = self.core.process(text, *labels)
        return doc

    def save_entity(self, entity: Entity):
        self.core.add(entity)

    def save_resource(self, resource: Resource):
        pass

    def save_relationship(self, a: Node, tag: str, b: Node) -> Relationship:
        pass

    def commit(self):
        self.core.commit()
