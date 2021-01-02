import os
from pathlib import Path

import pytest
from entitykb.config import Config, generate_secret
from entitykb.deps import EnvironError
from entitykb.env import Environ


def test_no_repeat():
    assert generate_secret() != generate_secret()
    assert len(generate_secret()) == 64


def test_environ_defaults():
    assert "ENTITYKB_ROOT" not in os.environ
    assert "ENTITYKB_RPC_PORT" not in os.environ

    environ = Environ()
    assert os.path.expanduser("~/.entitykb") == environ.root
    assert "ENTITYKB_ROOT" in os.environ
    assert "ENTITYKB_RPC_PORT" not in os.environ

    environ.commit()
    assert "ENTITYKB_RPC_PORT" in os.environ


def test_environ_set_get():
    environ = Environ()
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

    environ.mv_split = "|"
    assert environ.mv_split == "|"

    with pytest.raises(EnvironError):
        environ.root = "/will/fail"


def test_config_defaults():
    config = Config()
    assert config.dict() == {
        "graph": "entitykb.Graph",
        "modules": [],
        "normalizer": "entitykb.LatinLowercaseNormalizer",
        "pipelines": {
            "default": {
                "extractor": "entitykb.DefaultExtractor",
                "filterers": [],
                "resolvers": ["entitykb.TermResolver"],
            }
        },
        "searcher": "entitykb.DefaultSearcher",
        "secret_key": config.secret_key,
        "tokenizer": "entitykb.WhitespaceTokenizer",
        "user_store": "entitykb.UserStore",
    }


def test_config_roundtrip():
    config = Config()
    data = config.dict()
    assert set(data.keys()) == {
        "graph",
        "modules",
        "normalizer",
        "pipelines",
        "searcher",
        "secret_key",
        "tokenizer",
        "user_store",
    }

    roundtrip = Config(file_path="/tmp/config.json", **data)
    assert roundtrip.dict() == config.dict()


def test_get_root_dir():
    assert Path("/tmp") == Config.get_root(Path("/tmp"))
    assert isinstance(Config.get_root(None), Path)
