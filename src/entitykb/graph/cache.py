import sqlite3

import diskcache
from msgpack import packb, unpackb


class MsgPackDisk(diskcache.Disk):
    def __init__(self, directory, **kwargs):
        self.encoder = None
        self.decoder = None
        super().__init__(directory, **kwargs)

    def put(self, key):
        type_key = type(key)

        if type_key is bytes:
            return sqlite3.Binary(key), True
        elif (
            (type_key is str)
            or (
                type_key is int
                and -9223372036854775808 <= key <= 9223372036854775807
            )
            or (type_key is float)
        ):
            return key, True
        else:
            data = packb(key, default=self.encoder)
            return sqlite3.Binary(data), False

    def get(self, key, raw):
        if raw:
            return bytes(key) if type(key) is sqlite3.Binary else key
        else:
            return unpackb(key, object_hook=self.decoder)

    def store(self, value, read, key=diskcache.UNKNOWN):
        if not read:
            value = packb(value, default=self.encoder)
        return super(MsgPackDisk, self).store(value, read)

    def fetch(self, mode, filename, value, read):
        data = super(MsgPackDisk, self).fetch(mode, filename, value, read)
        if not read:
            data = unpackb(data, object_hook=self.decoder)
        return data


class MsgPackCache(diskcache.Cache):
    def __init__(self, directory, encoder, decoder, **kwargs):
        super().__init__(directory=directory, disk=MsgPackDisk, **kwargs)
        self.disk.encoder = encoder
        self.disk.decoder = decoder


def create_index(directory, encoder, decoder) -> diskcache.Index:
    cache = MsgPackCache(directory, encoder, decoder)
    return diskcache.Index.fromcache(cache=cache)
