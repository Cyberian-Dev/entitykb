import datetime
import os
import pickle
import sys
import tempfile
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, Any

from entitykb import logger, create_component


@dataclass
class Storage(object):
    root: Path
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
        backup_dir = self.root / "backups"
        if not backup_dir.exists():
            os.makedirs(backup_dir, exist_ok=True)
        return backup_dir

    @classmethod
    def create(cls, value=None, **kwargs):
        return create_component(value, Storage, PickleStorage, **kwargs)


@dataclass
class PickleStorage(Storage):
    def info(self) -> dict:
        last_commit = self.file_updated(self.index_path)
        return {
            "path": self.index_path,
            "disk_space": self.sizeof(self.index_path),
            "last_commit": last_commit and last_commit.strftime("%c"),
        }

    @property
    def index_path(self):
        if self.root:
            return self.root / "index.db"

    @property
    def exists(self):
        return self.index_path and self.index_path.exists()

    def load(self) -> Any:
        py_data = None

        if self.exists:
            with open(self.index_path, "rb") as fp:
                pickle_data = fp.read()
                try:
                    py_data = pickle.loads(pickle_data)

                except (AttributeError, pickle.UnpicklingError, TypeError):
                    logger.error(f"Failed to load index: {self.index_path}")

        return py_data

    def save(self, py_data: Any):
        pickle_data = pickle.dumps(py_data)
        self.safe_write(self.index_path, pickle_data)

    def archive(self):
        if self.exists and self.max_backups:
            path = self.index_path
            update_time = self.file_updated(path)
            file_name = os.path.basename(path)
            file_name += update_time.strftime(".%d-%m-%Y_%I-%M-%S.%f_%p")
            backup_path = self.backup_dir / file_name
            os.rename(path, backup_path)

            self.clean_backups()

    def clean_backups(self) -> Optional[str]:
        paths = [f"{self.backup_dir}/{x}" for x in os.listdir(self.backup_dir)]
        paths = sorted(paths, key=os.path.getctime)

        if len(paths) > self.max_backups:
            oldest = paths[0]
            os.remove(oldest)
            return oldest

    @classmethod
    def file_updated(cls, path: Path) -> datetime:
        if path and path.exists():
            file_t = os.path.getmtime(path)
            return datetime.datetime.fromtimestamp(file_t)

    @classmethod
    def sizeof_fmt(cls, num, suffix="B"):
        # https://stackoverflow.com/a/1094933/1946790
        val = None
        for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
            if abs(num) < 1024.0:
                val = "%.2f %s%s" % (num, unit, suffix)
                break
            num /= 1024.0
        val = val or "%.2f %s%s" % (num, "Yi", suffix)
        return val

    @classmethod
    def sizeof(cls, path_or_obj):
        if isinstance(path_or_obj, Path) and path_or_obj.exists():
            num = os.path.getsize(path_or_obj)
        else:
            num = sys.getsizeof(path_or_obj)
        return cls.sizeof_fmt(num)

    @classmethod
    def safe_write(cls, path: Path, data: bytes):
        """ Write data to temp file. Then use os.link to move into place. """
        # https://stackoverflow.com/a/36784658/1946790
        # https://stackoverflow.com/a/57015098/1946790
        with tempfile.NamedTemporaryFile(dir=path.parent, mode="w+b") as tf:
            tf.write(data)
            os.link(tf.name, path)
