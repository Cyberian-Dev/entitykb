import asyncio
from dataclasses import dataclass
from os import getenv as env

from aiorpc import RPCClient

from entitykb.utils import first_nn


@dataclass
class RPCConnection(object):
    host: str = None
    port: int = None
    timeout: int = None
    retries: int = 5
    rpc_client: RPCClient = None

    def __post_init__(self):
        self.host = first_nn(self.host, env("ENTITYKB_RCP_HOST", "0.0.0.0"))
        self.port = first_nn(self.port, env("ENTITYKB_RCP_HOST", 3477))
        self.timeout = first_nn(self.timeout, env("ENTITYKB_RCP_TIMEOUT", 60))

    def __str__(self):
        return f"tcp://{self.host}:{self.port}"

    async def __aenter__(self):
        if self.rpc_client is None:
            self.rpc_client = RPCClient(
                host=self.host, port=self.port, timeout=self.timeout
            )

        last_e = None
        for retry in range(self.retries):
            try:
                return await self.rpc_client.__aenter__()
            except OSError as e:
                await asyncio.sleep(retry // 10.0)
                last_e = e

        raise last_e

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.rpc_client.__aexit__(exc_type, exc_val, exc_tb)
