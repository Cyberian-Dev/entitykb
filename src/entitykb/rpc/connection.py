import asyncio
from dataclasses import dataclass
from typing import Optional

from aio_msgpack_rpc import Client
from msgpack import Packer, Unpacker

from entitykb import environ


@dataclass
class RPCConnection(object):
    host: str = None
    port: int = None
    timeout: int = None
    retries: int = None
    _client: Optional[Client] = None

    def __post_init__(self):
        self.host = self.host or environ.rpc_host
        self.port = self.port or environ.rpc_port
        self.timeout = self.timeout or environ.rpc_timeout
        self.retries = self.retries or environ.rpc_retries

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
        last_e = None
        for retry in range(self.retries):
            try:
                if self._client is None:
                    raise ConnectionRefusedError

                response = await self._client.call(name, *args, **kwargs)
                return response

            except Exception as e:
                await asyncio.sleep(retry / 10.0)
                await self.open()
                last_e = e

        raise last_e
