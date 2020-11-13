import codecs
from string import ascii_lowercase, digits, punctuation

import translitcodec
from entitykb import create_component


class Normalizer(object):
    def __call__(self, text: str):
        return self.normalize(text)

    @property
    def trie_characters(self) -> str:
        raise NotImplementedError

    def normalize(self, text: str):
        raise NotImplementedError

    @classmethod
    def create(cls, value=None):
        return create_component(value, Normalizer, LatinLowercaseNormalizer)


class LatinLowercaseNormalizer(Normalizer):
    """ Normalizes to lowercase ascii characters only. """

    def __init__(self):
        self._chars = ascii_lowercase + digits + punctuation + " "

    @property
    def trie_characters(self) -> str:
        return self._chars

    def normalize(self, text: str):
        text = codecs.encode(text, "transliterate")
        text = text.lower()
        return text


assert translitcodec
