from pytest import fixture, raises
from entitykb import Auth, exceptions, StoredUser, User, UserStatus, security


@fixture
def auth(root):
    return Auth(root=root, secret_key="0" * 64)


def test_get_words():
    assert len(security.get_words()) > 1000
    assert "abacus" == security.get_words()[0]
    assert "zoom" == security.get_words()[-1]


def test_generate_password():
    assert 3 == security.generate_password().count("-")
    assert len(security.generate_password()) > 15


def test_add_user(auth: Auth):
    password = auth.add_user(username="ian", status=UserStatus.read_write)
    assert len(password) > 15 and 3 == password.count("-")

    user: StoredUser = auth.get_user("ian")
    assert user.username == "ian"
    assert isinstance(user.uuid, str) and len(user.uuid) == 36
    assert user.hashed_password is not None
    assert user.status == UserStatus.read_write
    assert user.status.can_read
    assert user.status.can_write


def test_add_authenticate(auth: Auth):
    password = auth.add_user(username="ian", status=UserStatus.read_write)
    user: User = auth.authenticate(username="ian", password=password)

    assert user.username == "ian"
    assert isinstance(user.uuid, str) and len(user.uuid) == 36
    assert user.status == UserStatus.read_write
    assert user.status.can_read
    assert user.status.can_write


def test_set_status(auth: Auth):
    auth.add_user(username="ian", status=UserStatus.read_only)

    user: StoredUser = auth.get_user("ian")
    assert user.username == "ian"
    assert user.status == UserStatus.read_only
    assert user.status.can_read
    assert not user.status.can_write

    auth.set_status(username="ian", status=UserStatus.read_write)

    user: StoredUser = auth.get_user("ian")
    assert user.status.can_write


def test_reset_password(auth: Auth):
    pass_1 = auth.add_user(username="ian", status=UserStatus.read_write)

    pass_2 = auth.reset_password(username="ian")
    assert len(pass_2) > 15 and 3 == pass_2.count("-")
    assert pass_1 != pass_2


def test_invalid_user(auth: Auth):
    with raises(exceptions.InvalidUsername):
        auth.add_user(username="", status=UserStatus.read_write)

    auth.add_user(username="ian", status=UserStatus.read_write)
    with raises(exceptions.DuplicateUsername):
        auth.add_user(username="ian", status=UserStatus.read_write)
