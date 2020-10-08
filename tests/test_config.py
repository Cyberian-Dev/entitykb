from pathlib import Path
from entitykb.config import Config


def test_config_defaults():
    config = Config()
    assert config.dict() == {}


def test_config_roundtrip():
    config = Config(extractor="my_custom.Extractor")
    data = config.dict()
    assert set(data.keys()) == {"extractor"}

    roundtrip = Config.construct(file_path="/tmp/config.json", data=data)
    assert roundtrip.dict() == config.dict()


def test_get_root_dir():
    assert str(Path("/tmp").resolve()) == Config.get_root_dir(Path("/tmp"))
    assert isinstance(Config.get_root_dir(None), str)
