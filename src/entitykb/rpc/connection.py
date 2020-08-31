import asyncio
from dataclasses import dataclass
from os import getenv as env

from aio_msgpack_rpc import Client

from entitykb.utils import first_nn


@dataclass
class RPCConnection(object):
    host: str = None
    port: int = None
    timeout: float = None
    retries: int = None
    _client: Client = None

    def __post_init__(self):
        self.host = first_nn(self.host, env("ENTITYKB_RCP_HOST", "0.0.0.0"))
        self.port = first_nn(self.port, env("ENTITYKB_RCP_HOST", 3477))
        self.timeout = first_nn(self.timeout, env("ENTITYKB_RCP_TIMEOUT", 2))
        self.retries = first_nn(self.retries, env("ENTITYKB_RCP_RETRIES", 10))

    def __str__(self):
        return f"tcp://{self.host}:{self.port}"

    async def open(self):
        read, write = await asyncio.open_connection(self.host, self.port)
        self._client = Client(read, write, response_timeout=self.timeout)

    async def __aenter__(self):
        if self._client is None:
            await self.open()

        return self

    async def __aexit__(self, *_):
        pass

    async def call(self, name: str, *args):
        last_e = None
        for retry in range(self.retries):
            try:
                response = await self._client.call(name, *args)
                return response

            except Exception as e:
                await asyncio.sleep(retry / 10.0)
                await self.open()
                last_e = e

        raise last_e
