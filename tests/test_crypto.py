from entitykb import crypto


def test_get_words():
    assert len(crypto.get_words()) > 1000
    assert "abacus" == crypto.get_words()[0]
    assert "zoom" == crypto.get_words()[-1]


def test_generate_password():
    assert 3 == crypto.generate_password().count("-")
    assert len(crypto.generate_password()) > 15


def test_encode_decode_jwt():
    secret_key = crypto.generate_secret(32)
    subject = "want to know a secret?"

    token = crypto.encode_jwt_token(subject, secret_key=secret_key)
    assert isinstance(token, str)

    returned = crypto.decode_jwt_token(token, secret_key=secret_key)
    assert returned == subject
