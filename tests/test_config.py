from pathlib import Path
from entitykb.config import Config


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
