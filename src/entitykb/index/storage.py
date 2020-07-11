import os
import pickle
from dataclasses import dataclass
from typing import Optional, Any

from entitykb import utils, logger


@dataclass
class Storage(object):
    root_dir: str = None
    max_backups: int = 5

    def info(self) -> dict:
        raise NotImplementedError

    @property
    def exists(self):
        raise NotImplementedError

    def load(self) -> Any:
        raise NotImplementedError

    def save(self, py_data: Any):
        raise NotImplementedError

    def archive(self):
        raise NotImplementedError

    @property
    def backup_dir(self):
        backup_dir = os.path.join(self.root_dir, "backups")
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir, exist_ok=True)
        return backup_dir


@dataclass
class DefaultStorage(Storage):
    def info(self) -> dict:
        return {
            "path": self.index_path,
            "disk_space": utils.sizeof(self.index_path),
            "last_commit": utils.file_updated(self.index_path),
        }

    @property
    def index_path(self):
        if self.root_dir:
            return os.path.join(self.root_dir, "index.db")

    @property
    def exists(self):
        return self.index_path and os.path.exists(self.index_path)

    def load(self) -> Any:
        py_data = None

        if self.exists:
            with open(self.index_path, "rb") as fp:
                pickle_data = fp.read()
                try:
                    py_data = pickle.loads(pickle_data)

                except AttributeError:
                    logger.error("Failed to load index: " + self.index_path)

        return py_data

    def save(self, py_data: Any):
        pickle_data = pickle.dumps(py_data)
        utils.safe_write(self.index_path, pickle_data)

    def archive(self):
        if self.exists and self.max_backups:
            path = self.index_path
            update_time = utils.file_updated(path)
            file_name = os.path.basename(path)
            file_name += update_time.strftime(".%d-%m-%Y_%I-%M-%S_%p")
            backup_path = os.path.join(self.backup_dir, file_name)
            os.rename(path, backup_path)

            self.clean_backups()

    def clean_backups(self) -> Optional[str]:
        paths = [f"{self.backup_dir}/{x}" for x in os.listdir(self.backup_dir)]
        paths = sorted(paths, key=os.path.getctime)

        if len(paths) >= self.max_backups:
            oldest = paths[0]
            os.remove(oldest)
            return oldest
