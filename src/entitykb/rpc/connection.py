import asyncio
from dataclasses import dataclass
from typing import Optional

from aio_msgpack_rpc import Client
from msgpack import Packer, Unpacker

from entitykb import environ, logger


@dataclass
class RPCConnection(object):
    host: str = None
    port: int = None
    timeout: int = None
    _client: Optional[Client] = None

    def __post_init__(self):
        self.host = self.host or environ.rpc_host
        self.port = self.port or environ.rpc_port
        self.timeout = self.timeout or environ.rpc_timeout

    def __str__(self):
        return f"tcp://{self.host}:{self.port}"

    async def open(self):
        read, write = await asyncio.open_connection(self.host, self.port)
        self._client = Client(
            read,
            write,
            packer=Packer(use_bin_type=True, datetime=True),
            unpacker=Unpacker(raw=False, timestamp=3),
            response_timeout=self.timeout,
        )

    def close(self):
        self._client.close()

    async def __aenter__(self):
        if self._client is None:
            try:
                await self.open()
            except ConnectionRefusedError:
                self._client = None

        return self

    async def __aexit__(self, *_):
        pass

    async def call(self, name: str, *args, **kwargs):
        try:
            return await self._client.call(name, *args, **kwargs)
        except asyncio.TimeoutError:
            self._client = None
            logger.error(f"RPC Client Call Timeout: {name}")
