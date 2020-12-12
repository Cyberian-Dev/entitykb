import codecs
from string import ascii_lowercase, digits, punctuation

import translitcodec

from entitykb import interfaces


class LatinLowercaseNormalizer(interfaces.INormalizer):
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
