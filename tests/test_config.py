from entitykb.config import Config


def test_config_defaults():
    config = Config()
    assert len(config.resolvers) == 1
    assert config.tokenizer == "entitykb.DefaultTokenizer"


def test_config_roundtrip():
    config = Config()
    data = config.dict()
    assert set(data.keys()) == {
        "extractor",
        "filterers",
        "index",
        "normalizer",
        "resolvers",
        "tokenizer",
    }

    roundtrip = Config.construct(file_path="/tmp/config.json", data=data)
    assert isinstance(roundtrip.resolvers[0], str)
    assert roundtrip.dict() == config.dict()
