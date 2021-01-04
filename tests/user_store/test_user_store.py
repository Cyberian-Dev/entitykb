from pytest import fixture, raises

from entitykb import exceptions, StoredUser, UserStatus, UserStore


@fixture
def user_store(root):
    return UserStore(root=root, secret_key="0" * 64)


def test_add_user(user_store: UserStore):
    password = user_store.add_user(
        username="one", status=UserStatus.read_write
    )
    assert len(password) > 15 and 3 == password.count("-")

    user: StoredUser = user_store.find_by_username("one")
    assert user.username == "one"
    assert isinstance(user.uuid, str) and len(user.uuid) == 36
    assert user.hashed_password is not None
    assert user.status == UserStatus.read_write
    assert user.status.can_read
    assert user.status.can_write


def test_add_user_auth(user_store: UserStore):
    pw = user_store.add_user(username="one", status=UserStatus.read_write)
    token = user_store.authenticate(username="one", password=pw)
    user = user_store.get_user(token=token)
    assert user.status.can_write
    assert user.username == "one"


def test_set_status(user_store: UserStore):
    user_store.add_user(username="one", status=UserStatus.read_only)

    user: StoredUser = user_store.find_by_username("one")
    assert user.username == "one"
    assert user.status == UserStatus.read_only
    assert user.status.can_read
    assert not user.status.can_write

    user_store.set_status(username="one", status=UserStatus.read_write)

    user: StoredUser = user_store.find_by_username("one")
    assert user.status.can_write


def test_reset_password(user_store: UserStore):
    pass_1 = user_store.add_user(username="one", status=UserStatus.read_write)

    pass_2 = user_store.reset_password(username="one")
    assert len(pass_2) > 15 and pass_2.count("-") >= 3  # t-shirt!
    assert pass_1 != pass_2


def test_invalid_user(user_store: UserStore):
    with raises(exceptions.InvalidUsername):
        user_store.add_user(username="", status=UserStatus.read_write)

    user_store.add_user(username="one", status=UserStatus.read_write)
    with raises(exceptions.DuplicateUsername):
        user_store.add_user(username="one", status=UserStatus.read_write)


def test_add_user_list(user_store: UserStore):
    user_store.add_user(username="one", status=UserStatus.read_only)
    user_store.add_user(username="two", status=UserStatus.read_write)
    users = user_store.get_user_list()

    assert 2 == len(users)

    assert users[0].username == "one"
    assert not users[0].status.can_write

    assert users[1].username == "two"
    assert users[1].status.can_write
