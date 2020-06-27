from string import ascii_lowercase, digits, punctuation
from typing import Optional, Union, Type

import translitcodec
import codecs

from .utils import instantiate_class_from_name


class Normalizer(object):
    def __call__(self, text: str):
        return self.normalize(text)

    @property
    def trie_characters(self) -> str:
        raise NotImplementedError

    def normalize(self, text: str):
        raise NotImplementedError

    @classmethod
    def create(cls, normalizer=None):
        if normalizer is None:
            normalizer = DefaultNormalizer()
        elif isinstance(normalizer, str):
            normalizer = instantiate_class_from_name(normalizer)
        elif not isinstance(normalizer, Normalizer):
            normalizer = normalizer()
        return normalizer


class DefaultNormalizer(Normalizer):
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


NormalizerType = Optional[Union[Type[Normalizer], Normalizer, str]]

assert translitcodec
