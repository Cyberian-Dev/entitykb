import os
import time
from entitykb import PickleStorage


def test_backup_dirs(root):
    expected = os.path.join(root, "backups")
    assert os.path.exists(expected) is False

    storage = PickleStorage(root=root)
    assert expected == storage.backup_dir
    assert os.path.exists(expected)


def test_info(root):
    storage = PickleStorage(root=root)
    info = storage.info()
    assert {"path", "disk_space", "last_commit"} == info.keys()
    assert os.path.join(root, "index.db") == storage.index_path
    assert os.path.join(root, "index.db") == info["path"]


def test_save_load(root):
    storage = PickleStorage(root=root)
    assert storage.exists is False

    # good save
    storage.save("test")
    assert "test" == storage.load()

    # bad pickle save
    file_obj = open(storage.index_path, mode="w+b")
    file_obj.write(b"back-pickle")
    file_obj.close()

    assert storage.load() is None


def test_archive_clean_backups(root):
    storage = PickleStorage(root=root)
    assert 5 == storage.max_backups

    for i in range(storage.max_backups + 5):
        paths = os.listdir(storage.backup_dir)
        assert min(i, storage.max_backups) == len(paths), f"What? {paths} {i}"

        assert storage.exists is False
        storage.save(i)

        assert storage.exists is True
        assert i == storage.load()

        storage.archive()
        time.sleep(0.0001)

    assert storage.max_backups == len(os.listdir(storage.backup_dir))


def test_sizeof(root):
    assert PickleStorage.sizeof({}) == "248.00 B"
    assert PickleStorage.sizeof("abc") == "52.00 B"
    assert PickleStorage.sizeof("a" * 1000) == "1.02 KiB"

    storage = PickleStorage(root=root)
    storage.save("abc")
    assert PickleStorage.sizeof(storage.index_path) == "13.00 B"
