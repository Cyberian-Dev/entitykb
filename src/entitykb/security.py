import secrets
from pathlib import Path

from passlib.context import CryptContext
from smart_open import smart_open

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


def generate_secret(length=32):
    return secrets.token_hex(length)


def verify_password(password, hashed_password):
    return one_way_hash.verify(password, hashed_password)


def hash_password(password):
    return one_way_hash.hash(password)
