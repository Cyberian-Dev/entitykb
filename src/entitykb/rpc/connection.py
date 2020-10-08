import asyncio
from dataclasses import dataclass
from os import getenv as env

from aio_msgpack_rpc import Client


@dataclass
class RPCConnection(object):
    host: str = None
    port: int = None
    timeout: float = None
    retries: int = None
    _client: Client = None

    def __post_init__(self):
        self.host = first_nn(self.host, env("ENTITYKB_RCP_HOST", "localhost"))
        self.port = first_nn(self.port, env("ENTITYKB_RCP_HOST", 3477))
        self.timeout = first_nn(self.timeout, env("ENTITYKB_RCP_TIMEOUT", 2))
        self.retries = first_nn(self.retries, env("ENTITYKB_RCP_RETRIES", 5))

    def __str__(self):
        return f"tcp://{self.host}:{self.port}"

    async def open(self):
        read, write = await asyncio.open_connection(self.host, self.port)
        self._client = Client(read, write, response_timeout=self.timeout)

    async def __aenter__(self):
        if self._client is None:
            try:
                await self.open()
            except ConnectionRefusedError:
                self._client = None

        return self

    async def __aexit__(self, *_):
        pass

    async def call(self, name: str, *args):
        last_e = None
        for retry in range(self.retries):
            try:
                if self._client is None:
                    raise ConnectionRefusedError

                response = await self._client.call(name, *args)
                return response

            except Exception as e:
                await asyncio.sleep(retry / 10.0)
                await self.open()
                last_e = e

        raise last_e


def first_nn(*items):
    """ Returns first not None item. Lazy creates list, set, tuple, dict. """
    for item in items:
        if item is not None:
            if isinstance(item, type):
                return item()
            else:
                return item
