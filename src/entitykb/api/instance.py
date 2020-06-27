from entitykb import load, KB


class Instance(object):
    _instance = None

    @classmethod
    def get(cls) -> KB:
        if cls._instance is None:
            cls._instance = load()
        return cls._instance
