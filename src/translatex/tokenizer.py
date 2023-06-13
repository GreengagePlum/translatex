import re
from typing import Dict

from marker import Marker


class Tokenizer:
    DEFAULT_INITIAL_TOKEN_INDEX: int = 0
    DEFAULT_INITIAL_TOKEN_SUBINDEX: int = 0
    DEFAULT_TOKEN_SUBLIMIT: int = 16
    DEFAULT_TOKEN_FORMAT: str = "[{},{}]"

    def __init__(self, marked_string: str, marker_format: str = Marker.DEFAULT_MARKER_FORMAT) -> None:
        self._base_string: str = marked_string
        self._marked_string: str = marked_string
        self._tokenized_string: str = str()
        self._token_count: int = Tokenizer.DEFAULT_INITIAL_TOKEN_INDEX
        self._token_subcount: int = Tokenizer.DEFAULT_INITIAL_TOKEN_SUBINDEX
        self._token_sublimit: int = Tokenizer.DEFAULT_TOKEN_SUBLIMIT
        self.token_format: str = Tokenizer.DEFAULT_TOKEN_FORMAT
        self._marker_format: str = marker_format
        self._token_store: Dict[int, str] = dict()

    def __str__(self) -> str:
        return "The tokenizer format is {} and tokenizer count is at {}.".format(self._token_format,
                                                                                 self.total_token_count())

    def total_token_count(self) -> int:
        return self._token_count * self._token_sublimit + self._token_subcount

    def _next_token(self) -> str:
        if self._token_subcount >= self._token_sublimit:
            self._token_subcount = 0
            self._token_count += 1
        else:
            self._token_subcount += 1
        return self.token_format.format(self._token_count, self._token_subcount)

    @property
    def marked_string(self) -> str:
        """This property contains currently marked string that was once correct LaTeX"""
        return self._marked_string

    @marked_string.setter
    def marked_string(self, marked_string: str) -> None:
        """If this property is set, tokenized string, and all tokenizer related stuff gets reset so that everything is
        in sync"""
        self._marked_string = marked_string
        self._tokenized_string = str()
        self._token_count = Tokenizer.DEFAULT_INITIAL_TOKEN_INDEX
        self._token_subcount = Tokenizer.DEFAULT_INITIAL_TOKEN_SUBINDEX
        self._token_store = dict()

    @property
    def tokenized_string(self) -> str:
        """This property contains the tokenized, ready to translate string after tokenization operations."""
        return self._tokenized_string

    @tokenized_string.setter
    def tokenized_string(self, tokenized_string: str) -> None:
        """If this property is set, marked string gets reset so that everything is in sync"""
        self._tokenized_string = tokenized_string
        self._marked_string = str()

    @property
    def base_string(self) -> str:
        """The starting marked string. Saved aside so the original source is kept intact and accessible if need be."""
        return self._base_string

    @base_string.setter
    def base_string(self, base_string: str) -> None:
        """If the base changes, almost everything is reset and readied for the new base so that everything is in sync"""
        self._base_string = self._marked_string = base_string
        self._tokenized_string = str()
        self._token_count = Tokenizer.DEFAULT_INITIAL_TOKEN_INDEX
        self._token_subcount = Tokenizer.DEFAULT_INITIAL_TOKEN_SUBINDEX
        self._token_store = dict()

    @property
    def token_format(self) -> str:
        """The format string for tokens to be used."""
        return self._token_format

    @token_format.setter
    def token_format(self, format_str: str) -> None:
        """Set token format to be used.

        Args:
            format_str: A string that can be used with ``.format()``

        Raises:
            ValueError: If the given string doesn't have at least two occurrences of two empty curly braces "{}"

        """
        pattern = r'\{\}'
        matches = re.findall(pattern, format_str, re.DOTALL)
        if len(matches) < 2:
            raise ValueError("Not enough empty curly braces in the given format string")
        self._token_format = format_str

    def _tokenize_named_envs(self, process_string: str) -> str:
        marker_regex = self._marker_format.format(r"(?:\d+)")
        pattern = re.compile(r"(?:\\begin|\\end)\{" + marker_regex + r"\}(\[.*\])*")
        current_string = process_string
        all_replaced = False
        while not all_replaced:
            current_string, replace_count = pattern.subn(self._next_token(), current_string, 1)
            if replace_count == 0:
                all_replaced = True
        return current_string

    def _tokenize_commands(self, process_string: str) -> str:
        marker_regex = self._marker_format.format(r"(?:\d+)")
        pattern = re.compile(r"\\" + marker_regex + r"(?:\[.*\])*(\{.*\})(?:\[.*\])*")
        current_string = process_string
        all_replaced = False
        while not all_replaced:
            current_string, replace_count = pattern.subn(self._next_token() + r"\1", current_string, 1)
            if replace_count == 0:
                all_replaced = True
        return current_string

    def tokenize(self):
        current_string: str = self._marked_string
        current_string = self._tokenize_named_envs(current_string)
        current_string = self._tokenize_commands(current_string)
        # to be continued...
        self._tokenized_string = current_string


with open("../../examples/translatex.tex") as f:
    m = Marker(f.read())

m.do_marking()
t = Tokenizer(m.marked_latex)
t.tokenize()

with open("../../examples/translatex_post.tex", "w+") as f:
    f.write(m.marked_latex)
with open("../../examples/translatex_post2.tex", "w+") as f:
    f.write(t.tokenized_string)