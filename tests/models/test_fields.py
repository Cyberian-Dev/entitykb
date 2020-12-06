from entitykb.models.fields import SmartList


def test_smart_list():
    items = SmartList()
    assert len(items) == 0
    assert list(items) == []
