import os

from .deps import CheckEnviron


class Environ(CheckEnviron):
    class DEFAULTS:
        ENTITYKB_ROOT = os.path.expanduser("~/.entitykb")
        ENTITYKB_RPC_HOST = "localhost"
        ENTITYKB_RPC_PORT = 3477
        ENTITYKB_RPC_TIMEOUT = 2
        ENTITYKB_RPC_RETRIES = 5

    def commit(self):
        # lock in any environ variables that are not set
        for i in vars(self.DEFAULTS):
            if not i.startswith("_"):
                self.__getitem__(i)

    @property
    def root(self) -> str:
        return self["ENTITYKB_ROOT"]

    @root.setter
    def root(self, value: str):
        self["ENTITYKB_ROOT"] = value

    @property
    def rpc_host(self) -> str:
        return self["ENTITYKB_RPC_HOST"]

    @rpc_host.setter
    def rpc_host(self, value: str):
        self["ENTITYKB_RPC_HOST"] = value

    @property
    def rpc_port(self) -> int:
        return int(self["ENTITYKB_RPC_PORT"])

    @rpc_port.setter
    def rpc_port(self, value: int):
        self["ENTITYKB_RPC_PORT"] = str(value)

    @property
    def rpc_timeout(self) -> int:
        return int(self["ENTITYKB_RPC_TIMEOUT"])

    @rpc_timeout.setter
    def rpc_timeout(self, value: int):
        self["ENTITYKB_RPC_TIMEOUT"] = str(value)

    @property
    def rpc_retries(self) -> int:
        return int(self["ENTITYKB_RPC_RETRIES"])

    @rpc_retries.setter
    def rpc_retries(self, value: int):
        self["ENTITYKB_RPC_RETRIES"] = str(value)


environ = Environ()
