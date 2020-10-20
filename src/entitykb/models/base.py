import enum


class SlotBase(object):
    """ Each subclass must define __slots__ """

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __hash__(self):
        return hash((repr(self)))

    def __repr__(self):
        data = self.dict()
        items = sorted(f"{k}={v}" for k, v in data.items() if v is not None)
        return f"<{self.__class__.__name__}: {', '.join(items)}>"

    def dict(self):
        data = dict()

        for name in self.__slots__:
            value = getattr(self, name)
            value = self._dict_value(value)
            data[name] = value

        return data

    @classmethod
    def _dict_value(cls, value):
        if isinstance(value, SlotBase):
            return value.dict()

        if isinstance(value, (tuple, list, set)):
            return tuple([cls._dict_value(v) for v in value])

        if isinstance(value, enum.Enum):
            return value.value

        return value

    @classmethod
    def create(cls, _item=None, *, _klass=None, **kwargs):
        if _item is None and len(kwargs) == 0:
            return None

        if isinstance(_item, cls):
            return _item

        if isinstance(_item, dict):
            kwargs = {**_item, **kwargs}

        _klass = _klass or cls.identify_klass(kwargs)
        _klass = _klass or cls

        return _klass(**kwargs)

    @classmethod
    def identify_klass(cls, kwargs):
        return cls
