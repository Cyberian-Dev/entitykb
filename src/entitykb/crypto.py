import datetime
import secrets
from pathlib import Path

import jwt
from passlib.context import CryptContext
from smart_open import smart_open


# secret


def generate_secret(length=32):
    return secrets.token_hex(length)


# password

one_way_hash = CryptContext(schemes=["bcrypt"], deprecated="auto")
word_set = None


def get_words():
    global word_set
    if word_set is None:
        word_file = Path(__file__).parent / "deps" / "eff-long.txt.gz"
        word_set = smart_open(word_file, "r").read().splitlines()
    return word_set


def generate_password(count=4):
    password = "-".join(secrets.choice(get_words()) for _ in range(count))
    return password


def verify_password(password, hashed_password):
    return one_way_hash.verify(password, hashed_password)


def hash_password(password):
    return one_way_hash.hash(password)


# Javascript Web Tokens (JWT)

ALGORITHM = "HS256"
JWT_EXPIRE = "exp"
JWT_NOT_BEFORE = "nbf"
JWT_SUBJECT = "sub"


def decode_jwt_token(token: str, secret_key: str) -> str:
    payload = jwt.decode(token, secret_key, algorithms=[ALGORITHM])
    return payload[JWT_SUBJECT]


def encode_jwt_token(subject: str, secret_key: str) -> str:
    expires_in = datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    expires = (datetime.datetime.utcnow() + expires_in).timestamp()
    payload = {JWT_SUBJECT: subject, JWT_EXPIRE: int(expires)}
    encoded = jwt.encode(payload, secret_key, algorithm=ALGORITHM)
    encoded_str = encoded.decode("utf-8")
    return encoded_str


ACCESS_TOKEN_EXPIRE_DAYS = 14
ACCESS_TOKEN_EXPIRE_MINUTES = (60 * 24) * ACCESS_TOKEN_EXPIRE_DAYS
