import string
from typing import Optional, Union, Type, Iterator, Set, Iterable

from .model import Token, DocToken
from .utils import instantiate_class_from_name


class Tokenizer(object):
    def __call__(self, text: str) -> Iterator[Token]:
        return self.tokenize(text)

    def tokenize(self, text) -> Iterator[Token]:
        raise NotImplementedError

    def detokenize(self, tokens: Iterable[Token]) -> str:
        raise NotImplementedError

    def as_tuples(self, text):
        tuples = tuple((str(t), t.ws_after) for t in self(text))
        return tuples

    @classmethod
    def create(cls, tokenizer: "TokenizerType" = None):
        if isinstance(tokenizer, str):
            tokenizer = instantiate_class_from_name(tokenizer)
        elif not isinstance(tokenizer, Tokenizer):
            tokenizer = (tokenizer or DefaultTokenizer)()
        return tokenizer


class State(object):
    def __init__(self, word_chars: Set[str], whitespace: Set[str]):
        self.word_chars_set = word_chars
        self.whitespace_set = whitespace

        self.word_char = []
        self.ws_char = False
        self.other_char = None

        self.tokens = []

    def push(self, ch: str):
        if ch in self.word_chars_set:
            self.push_word_char(ch)
        elif ch in self.whitespace_set:
            self.push_whitespace()
        else:
            self.push_other(ch)

    def push_word_char(self, ch: str):
        self.bank_tokens()
        self.word_char.append(ch)

    def push_whitespace(self):
        self.ws_char = True

    def push_other(self, ch: str):
        self.bank_tokens()
        self.other_char = ch

    def mark_eol(self):
        self.do_bank()

    def bank_tokens(self):
        if self.ws_char or self.other_char:
            self.do_bank()

    def do_bank(self):
        ws_after = self.ws_char
        self.ws_char = False

        if self.word_char:
            data = "".join(self.word_char)
            self.word_char = []

            token = Token(data)
            token.ws_after = False if self.other_char else ws_after
            self.tokens.append(token)

        if self.other_char:
            token = Token(self.other_char)
            token.ws_after = ws_after
            self.tokens.append(token)
            self.other_char = None

    def __iter__(self) -> Iterator[Token]:
        tokens = []
        if self.tokens:
            tokens = self.tokens
            self.tokens = []
        return iter(tokens)


class DefaultTokenizer(Tokenizer):
    def __init__(
        self,
        word_chars: Optional[Set[str]] = None,
        whitespace: Optional[Set[str]] = None,
    ):
        self.word_chars = word_chars or DEFAULT_WORD_CHARS
        self.whitespace = whitespace or DEFAULT_WHITESPACE

    def tokenize(self, text) -> Iterator[Token]:
        state = State(self.word_chars, self.whitespace)

        for ch in text:
            state.push(ch)
            yield from state

        state.mark_eol()
        yield from state

    @classmethod
    def detokenize(cls, tokens: Iterable[Union[Token, DocToken]]) -> str:
        text = ""
        add_ws = False
        for token in tokens:
            if add_ws:
                text += " "
            token = token.token if isinstance(token, DocToken) else token
            text += token
            add_ws = token.ws_after
        return text


TokenizerType = Optional[Union[Type[Tokenizer], Tokenizer, str]]
DEFAULT_WORD_CHARS = set(string.digits + string.ascii_letters + "_" + "-")
DEFAULT_WHITESPACE = {" ", "\n", "\t"}
