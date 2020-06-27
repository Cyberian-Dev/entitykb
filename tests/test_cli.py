import entitykb.cli


def test_modules_imported():
    # todo: do we want to really unit test?
    assert entitykb.cli
    assert entitykb.cli.etl
