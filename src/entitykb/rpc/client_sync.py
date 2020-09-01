import asyncio

from entitykb.model import Doc, Entity, Resource, Relationship
from .client_async import AsyncKB


def run_future(future):
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(future)
    return result


class SyncKB(AsyncKB):
    """ EntityKB RPC Client """

    def parse(self, text, *labels) -> Doc:
        future = super(SyncKB, self).parse(text, *labels)
        doc = run_future(future)
        return doc

    def search(self, query):
        pass

    def suggest(self, query):
        pass

    def commit(self):
        future = super(SyncKB, self).commit()
        count = run_future(future)
        return count

    def reset(self):
        future = super(SyncKB, self).reset()
        success = run_future(future)
        return success

    def reload(self):
        pass

    def info(self):
        future = super(SyncKB, self).info()
        data = run_future(future)
        return data

    def save_entity(self, entity: Entity):
        future = super(SyncKB, self).save_entity(entity)
        doc = run_future(future)
        return doc

    def get_entity(self, key_or_id):
        pass

    def delete_entity(self, key_or_id):
        pass

    def save_resource(self, resource: Resource):
        pass

    def get_resource(self, key_or_id):
        pass

    def delete_resource(self, key_or_id):
        pass

    def save_relationship(self, relationship: Relationship):
        pass

    def delete_relationship(self, relationship: Relationship):
        pass
