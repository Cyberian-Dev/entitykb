import diskcache
from msgpack import packb, unpackb
from pydantic.json import pydantic_encoder


class MsgPackDisk(diskcache.Disk):
    def __init__(self, directory, **kwargs):
        self.encoder = None
        self.decoder = None
        super().__init__(directory, **kwargs)

    def put(self, key):
        return key, True

    def get(self, key, raw):
        return key

    def store(self, value, read, key=diskcache.UNKNOWN):
        if not read:
            if value is not None:
                value = packb(value, default=self.encoder)
        return super(MsgPackDisk, self).store(value, read)

    def fetch(self, mode, filename, value, read):
        data = super(MsgPackDisk, self).fetch(mode, filename, value, read)
        if not read:
            if data is not None:
                data = unpackb(data)
                data = self.decoder(**data) if self.decoder else data
        return data


class MsgPackCache(diskcache.Cache):
    def __init__(self, directory, encoder, decoder, **kwargs):
        super().__init__(directory=directory, disk=MsgPackDisk, **kwargs)
        self.disk.encoder = encoder
        self.disk.decoder = decoder


def create_index(directory, encoder=None, decoder=None) -> diskcache.Index:
    encoder = encoder or pydantic_encoder
    cache = MsgPackCache(directory, encoder, decoder)
    return diskcache.Index.fromcache(cache=cache)
