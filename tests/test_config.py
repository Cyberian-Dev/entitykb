import pytest
from pathlib import Path
from entitykb.config import Config, environ
from entitykb.deps import EnvironError


def test_environ_defaults():
    environ.root = "/opt/entitykb"
    assert environ.root == "/opt/entitykb"

    environ.rpc_host = "0.0.0.0"
    assert environ.rpc_host == "0.0.0.0"

    environ.rpc_port = 8001
    assert environ.rpc_port == 8001

    environ.rpc_timeout = 3
    assert environ.rpc_timeout == 3

    environ.rpc_retries = 10
    assert environ.rpc_retries == 10

    with pytest.raises(EnvironError):
        environ.root = "/will/fail"


def test_config_defaults():
    config = Config()
    assert config.dict() == {
        "extractor": "entitykb.DefaultExtractor",
        "filterers": (),
        "normalizer": "entitykb.DefaultNormalizer",
        "resolvers": ("entitykb.DefaultResolver",),
        "tokenizer": "entitykb.DefaultTokenizer",
    }


def test_config_roundtrip():
    config = Config(extractor="my_custom.Extractor")
    data = config.dict()
    assert set(data.keys()) == {
        "resolvers",
        "normalizer",
        "filterers",
        "extractor",
        "tokenizer",
    }

    roundtrip = Config.construct(file_path="/tmp/config.json", data=data)
    assert roundtrip.dict() == config.dict()


def test_get_root_dir():
    assert str(Path("/tmp").resolve()) == Config.get_root(Path("/tmp"))
    assert isinstance(Config.get_root(None), str)
