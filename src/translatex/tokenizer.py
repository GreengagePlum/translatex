"""Here is where all the marked LaTeX structures from the previous stage get tokenized.

This module houses all the logic to replace all the marked parts of a given former LaTeX string with the specified
token format. The string is finalized for transmission to an automatic translator where there is only the actual text
and the tokens left. The tokens are to be chosen in a way that won't disturb the translation nor get modified or removed
during the said process.
"""
import logging
from typing import TYPE_CHECKING, Dict

import regex as re

from .data import *
from .marker import Marker

if TYPE_CHECKING:
    from .translator import Translator

log = logging.getLogger("translatex.tokenizer")


class Tokenizer:
    """Tokenizer and detokenizer for marked LaTeX depending on the given marker and tokenizer formats.

    This process makes heavy use of regular expressions. It is linear and doesn't need recursion since that is handled
    in the previous marking stage. All strings replaced by tokens are stored in a dictionary for later reconstruction
    during detokenization. Structures with text to keep for translation are stored in a special way in the dictionary
    which is explained more in detail later.

    The Default token format is inspired by another similar but more primitive project called
    `gtexfix <https://github.com/drgulevich/gtexfix>`_.
    """

    DEFAULT_INITIAL_TOKEN_INDEX: int = 0
    DEFAULT_INITIAL_TOKEN_SUBINDEX: int = 0
    DEFAULT_TOKEN_SUBLIMIT: int = 16
    DEFAULT_TOKEN_FORMAT: str = "[{}-{}]"
    DEFAULT_DETOKENIZER_CONTENT_INDICATOR: str = "%%"

    def __init__(
        self,
        marked_string: str,
        marker_format: str = Marker.DEFAULT_MARKER_FORMAT,
    ) -> None:
        """Creates a Tokenizer with default settings.

        Args:
            marked_string: The string that contains marked LaTeX
            marker_format: The marker format used in the given marked string

        """
        self._base_string: str = marked_string
        self._marked_string: str = marked_string
        self._tokenized_string: str = str()
        self._token_count: int = Tokenizer.DEFAULT_INITIAL_TOKEN_INDEX
        """The major token number used in the token format with two numbers"""
        self._token_subcount: int = Tokenizer.DEFAULT_INITIAL_TOKEN_SUBINDEX
        """The minor token number used in the token format with two numbers"""
        self._token_sublimit: int = Tokenizer.DEFAULT_TOKEN_SUBLIMIT
        """The upper limit for the minor token number used in the token format with two numbers"""
        self.token_format: str = Tokenizer.DEFAULT_TOKEN_FORMAT
        self._marker_format: str = marker_format
        """The marker format used in the given marked string"""
        self._token_store: Dict[str, str] = dict()
        """The dictionary that associates the tokens to the strings that they replace"""

    @classmethod
    def from_marker(cls, marker: Marker) -> "Tokenizer":
        """Another constructor that creates a Tokenizer from a given Marker. For convenience."""
        return cls(marker.marked_latex, marker.marker_format)

    def update_from_translator(self, translator: "Translator") -> None:
        """A convenience method to update the tokenized string from a Translator."""
        self.tokenized_string = translator.translated_string

    def __str__(self) -> str:
        return f"The tokenizer format is {self._token_format} and tokenizer count is at {self.total_token_count()}."

    def total_token_count(self) -> int:
        """Gives the total number of tokens used after tokenization."""
        return self._token_count * self._token_sublimit + self._token_subcount

    def _next_token(self) -> str:
        if self._token_subcount >= self._token_sublimit:
            self._token_subcount = 0
            self._token_count += 1
        else:
            self._token_subcount += 1
        return self.token_format.format(
            self._token_count, self._token_subcount
        )

    @property
    def marked_string(self) -> str:
        """This property contains currently marked string that was once correct LaTeX.

        If this property is set, tokenized string, and all tokenizer-related stuff gets reset so that everything is
        in sync.
        """
        return self._marked_string

    @marked_string.setter
    def marked_string(self, marked_string: str) -> None:
        self._marked_string = marked_string
        self._tokenized_string = str()
        self._token_count = Tokenizer.DEFAULT_INITIAL_TOKEN_INDEX
        self._token_subcount = Tokenizer.DEFAULT_INITIAL_TOKEN_SUBINDEX
        self._token_store = dict()

    @property
    def tokenized_string(self) -> str:
        """This property contains the tokenized, ready to translate string after tokenization operations.

        If this property is set, marked string gets reset so that everything is in sync.
        """
        return self._tokenized_string

    @tokenized_string.setter
    def tokenized_string(self, tokenized_string: str) -> None:
        self._tokenized_string = tokenized_string
        self._marked_string = str()

    @property
    def base_string(self) -> str:
        """The starting marked string. Saved aside so the original source is kept intact and accessible if need be.

        If the base changes, almost everything is reset and readied for the new base so that everything is in sync
        """
        return self._base_string

    @base_string.setter
    def base_string(self, base_string: str) -> None:
        self._base_string = self._marked_string = base_string
        self._tokenized_string = str()
        self._token_count = Tokenizer.DEFAULT_INITIAL_TOKEN_INDEX
        self._token_subcount = Tokenizer.DEFAULT_INITIAL_TOKEN_SUBINDEX
        self._token_store = dict()

    @property
    def token_format(self) -> str:
        """The format string for tokens to be used.

        Raises:
            ValueError: If the given string doesn't have at least two occurrences of two empty curly braces "{}"
                since we're looking for a string that can be used with ``str.format()``.

        """
        return self._token_format

    @token_format.setter
    def token_format(self, format_str: str) -> None:
        Tokenizer.token_format_check(format_str)
        self._token_format = format_str

    @staticmethod
    def token_format_check(format_str: str) -> None:
        pattern = r"\{\}"
        matches = re.findall(pattern, format_str, re.DOTALL)
        if len(matches) < 2:
            raise ValueError(
                "Not enough empty curly braces in the given format string"
            )

    @staticmethod
    def token_regex(format_str: str) -> str:
        """Construct a regex corresponding to the given token format."""
        Tokenizer.token_format_check(format_str)
        first_curly_start = format_str.find(r"{}")
        second_curly_start = format_str.find(r"{}", first_curly_start + 2)
        escaped_token_format = (
            re.escape(format_str[:first_curly_start])
            + "{}"
            + re.escape(format_str[first_curly_start + 2 : second_curly_start])
            + "{}"
            + re.escape(format_str[second_curly_start + 2 :])
        )
        return escaped_token_format.format(r"(?:\d+)", r"(?:\d+)")

    def dump_store(self) -> str:
        string_transformed = [
            f"{item}\n" for item in self._token_store.items()
        ]
        return "".join(string_transformed)

    def _token_regex(self) -> str:
        """Construct a regex corresponding to the current instance token format."""
        return Tokenizer.token_regex(self._token_format)

    def _tokenize_completely_removed(self, process_string: str) -> str:
        """Tokenizes all structures listed as to be completely removed in the data module."""
        current_string = process_string
        for command in COMPLETELY_REMOVED_COMMANDS:
            # Explanation for the following regex: The command has to have at least a single pair of curly braces
            # following it. This can be located directly after the command or optionally be preceded by a set of
            # square brackets. It can also optionally be followed by a set of square brackets. If there is a pair
            # mismatch, regex fails (due to missing compliment, or backslash escaped opening and closing characters
            # respectively). Each group is recursive to be able to match the outermost pair and its complete
            # contents, which is why a pair mismatch is intolerable. Additionally, some tolerance is built-in. The
            # regex is hardened against backslash escaped opening characters which fail on an odd number of preceding
            # backslashes. All outermost pairs can have up to a single space between them since they don't have a
            # meaning in LaTeX in this case and can be coming across frequently with non-formatted/linted LaTeX files.
            # The regex stops on the encounter of the token format while matching curly braces and square brackets to
            # avoid tokenizing tokens.
            # fmt: off
            pattern = re.compile(
                r"\\" + command +
                r"(?<!\\)(?:\\\\)*(\s?(?!" + self._token_regex() + r")\[(?:[^\[\]]+|(?1))*\])*"
                r"(?<!\\)(?:\\\\)*(\s?(?!" + self._token_regex() + r")\{(?:[^{}]+|(?2))*\})+"
                r"(?<!\\)(?:\\\\)*(\s?(?!" + self._token_regex() + r")\[(?:[^\[\]]+|(?3))*\])*"
            )
            # fmt: on
            all_replaced = False
            while not all_replaced:
                match = pattern.search(current_string)
                if match:
                    next_token = self._next_token()
                    self._token_store.update({next_token: match[0]})
                    current_string, _ = pattern.subn(
                        next_token, current_string, 1
                    )
                else:
                    all_replaced = True
        return current_string

    def _tokenize_specials(self, process_string: str) -> str:
        """Tokenizes all special case structures listed in the data module.

        .. note::

            Not all special cases are processed so far.

        """
        current_string = process_string
        pattern = r"\\item"
        match = re.search(pattern, current_string)
        if match:
            next_token = self._next_token()
            self._token_store.update({next_token: match[0]})
            current_string = re.sub(pattern, next_token, current_string)
        pattern = re.compile(r"\\verb(\S).*\1")
        all_replaced = False
        while not all_replaced:
            match = pattern.search(current_string)
            if match:
                next_token = self._next_token()
                self._token_store.update({next_token: match[0]})
                current_string, _ = pattern.subn(next_token, current_string, 1)
            else:
                all_replaced = True
        return current_string

    def _tokenize_unnamed_math_optimized(self, process_string: str) -> str:
        """Tokenizes all unnamed math environments with slight optimizations allowing for a lesser number of tokens
        generated.

        If there is no text for translation, all is replaced with a single token. Otherwise, all from the beginning
        until the text to keep uses one token, all that is between the text to keep uses one token and everything at the
        end uses one token.
        """
        marker_regex = Marker.marker_regex(self._marker_format)
        pattern = re.compile(
            r"(?<!\\)(?:\\\\)*(\\\[|\\\(|\$|\$\$)(?:"
            + marker_regex
            + r"\s*)*(\\\]|\\\)|\$|\$\$)?"
        )
        current_string = process_string
        all_replaced = False
        while not all_replaced:
            match = pattern.search(current_string)
            if match:
                next_token = self._next_token()
                self._token_store.update({next_token: match[0]})
                current_string, _ = pattern.subn(next_token, current_string, 1)
            else:
                all_replaced = True
        pattern = re.compile(
            r"(?:" + marker_regex + r")*(?<!\\)(?:\\\\)*(\\\]|\\\)|\$|\$\$)"
        )
        all_replaced = False
        while not all_replaced:
            match = pattern.search(current_string)
            if match:
                next_token = self._next_token()
                self._token_store.update({next_token: match[0]})
                current_string, _ = pattern.subn(next_token, current_string, 1)
            else:
                all_replaced = True
        return current_string

    def _tokenize_commands(self, process_string: str) -> str:
        r"""Tokenizes all marked LaTeX commands that are of ``\<marker>{other}{other}{text to keep}`` format.

        Only leaves the contents of the last occurring pair of curly braces.

        While saving the replaced string to the dictionary, the last occurring pair of curly braces and its contents are
        replaced by an indicator to help with the detokenization later. This is done to easily spot where the new pair
        of curly braces that were just translated need to be put during reconstruction so that LaTeX is kept intact.

        .. warning::

            Doesn't include square braces in the regex for the time being but must be included some time later since
            commands can have options inside square braces which need to also be replaced by the token used.

        """
        marker_regex = Marker.marker_regex(self._marker_format)
        # fmt: off
        pattern = re.compile(
            r"\\" + marker_regex +
            r"(?<!\\)(?:\\\\)*(\s?(?!" + self._token_regex() + r")\[(?:[^\[\]]+|(?1))*\])*"
            r"(?<!\\)(?:\\\\)*(\s?(?!" + self._token_regex() + r")\{(?:[^{}]+|(?2))*\})*"
            r"(?<!\\)(?:\\\\)*(\s?(?!" + self._token_regex() + r")\{(?:[^{}]+|(?3))*\})?"
            r"(?<!\\)(?:\\\\)*(\s?(?!" + self._token_regex() + r")\[(?:[^\[\]]+|(?4))*\])*"
        )
        # fmt: on
        current_string = process_string
        all_replaced = False
        while not all_replaced:
            match = pattern.search(current_string)
            if match:
                next_token = self._next_token()
                if match[2]:
                    stored_string = (
                        match[0][: match.start(2) - match.start(0)]
                        + Tokenizer.DEFAULT_DETOKENIZER_CONTENT_INDICATOR
                        + match[0][match.end(2) - match.start(0) :]
                    )
                    self._token_store.update({next_token: stored_string})
                else:
                    self._token_store.update({next_token: match[0]})
                current_string, _ = pattern.subn(
                    next_token + r"\2", current_string, 1
                )
            else:
                all_replaced = True
        return current_string

    def _tokenize_named_envs(self, process_string: str) -> str:
        r"""Tokenizes all marked pairs of ``\begin{}...\end{}`` and their contents.

        The same small optimization as the unnamed math processor takes place here. If there is only a single marker
        inside a marked environment, all is replaced by a single token. Otherwise, tokens are used one by one for each
        range to be replaced without the text: from the start until some text, from that text until some other text and
        finally from that text until the very end.
        """
        marker_regex = Marker.marker_regex(self._marker_format)
        # fmt: off
        pattern = re.compile(
            r"\\begin\{" + marker_regex + r"\}"
            r"(?<!\\)(?:\\\\)*(\s?(?!" + self._token_regex() + r")\{(?:[^{}]+|(?1))*\})*"
            r"(?<!\\)(?:\\\\)*(\s?(?!" + self._token_regex() + r")\[(?:[^\[\]]+|(?2))*\])*"
            r"(?<!\\)(?:\\\\)*(\s?(?!" + self._token_regex() + r")\{(?:[^{}]+|(?3))*\})*"
            r"(?:\s*" + marker_regex + r"\s*)*"
            r"(?:\\end\{" + marker_regex + r"\})?"
        )
        # fmt: on
        current_string = process_string
        all_replaced = False
        while not all_replaced:
            match = pattern.search(current_string)
            if match:
                next_token = self._next_token()
                self._token_store.update({next_token: match[0]})
                current_string, _ = pattern.subn(next_token, current_string, 1)
            else:
                all_replaced = True
        pattern = re.compile(
            r"(?:\s*[^\\]"
            + marker_regex
            + r")*(?:\\end\{"
            + marker_regex
            + r"\})"
        )
        all_replaced = False
        while not all_replaced:
            match = pattern.search(current_string)
            if match:
                next_token = self._next_token()
                self._token_store.update({next_token: match[0]})
                current_string, _ = pattern.subn(next_token, current_string, 1)
            else:
                all_replaced = True
        return current_string

    def _tokenize_markers(self, process_string: str) -> str:
        r"""Here, only single markers are tokenized.

        This means only markers that indicate the contents of environments which are not preceded by backslashes (those
        would be command markers) or inside ``\begin{}...\end{}`` statements (these are named environment markers) are
        tokenized.
        """
        marker_regex = Marker.marker_regex(self._marker_format)
        pattern = re.compile(marker_regex)
        current_string = process_string
        all_replaced = False
        while not all_replaced:
            match = pattern.search(current_string)
            if match:
                next_token = self._next_token()
                self._token_store.update({next_token: match[0]})
                current_string, _ = pattern.subn(next_token, current_string, 1)
            else:
                all_replaced = True
        return current_string

    def _tokenize_comments(self, process_string: str) -> str:
        """All LaTeX single line comments are tokenized here."""
        pattern = re.compile(r"(?<!\\)(?:\\\\)*%.*$", re.MULTILINE)
        current_string = process_string
        all_replaced = False
        while not all_replaced:
            match = pattern.search(current_string)
            if match:
                next_token = self._next_token()
                self._token_store.update({next_token: match[0]})
                current_string, _ = pattern.subn(next_token, current_string, 1)
            else:
                all_replaced = True
        return current_string

    def _tokenize_latex_escapes(self, process_string: str) -> str:
        r"""All LaTeX backslash escapes are tokenized here such as ``\; \, \{``.

        This is done so that the string is further freed from potentially confusing sequences to the automatic
        translator.
        """
        current_string = process_string
        pattern = re.compile(r"(?:\\\S|\\)(?!\w)+")
        all_replaced = False
        while not all_replaced:
            match = re.search(pattern, current_string)
            if match:
                next_token = self._next_token()
                self._token_store.update({next_token: match[0]})
                current_string = re.sub(pattern, next_token, current_string, 1)
            else:
                all_replaced = True
        return current_string

    def tokenize(self) -> None:
        r"""Tokenizes the marked LaTeX string of the instance it is called on and places it in the tokenized string
        property.

        The tokenization is performed starting from the first occurrence of a marker until the end of the string. This
        allows for the tokenization to be performed only for the document (``\begin{document}``) and not for the header
        which is not to be automatically translated.

        According to the marker format of the instance, one by one (mostly from most specific to least specific to avoid
        interference), various subroutines that make heavy use of regular expressions are called to tokenize the marked
        string layer by layer. The result is then stored in the tokenized string instance variable.

        During this stage, thanks to the subroutines, all strings replaced by tokens are stored in the dictionary; thus
        it is populated after a call to this method (a first tokenization run).

        Raises:
            ValueError: If string to tokenize is empty.

        """
        marker_regex = Marker.marker_regex(self._marker_format)
        if not self._marked_string:
            raise ValueError("Marked string is empty, nothing to tokenize")
        split_strings: List[str] = re.split(
            r"(^.*" + marker_regex + r".*$)",
            self._marked_string,
            1,
            re.MULTILINE,
        )
        if len(split_strings) == 1:
            self._tokenized_string = self._marked_string
            log.warning("No markers found, tokenization halted")
            return
        header_string: str = split_strings[0]
        main_string: str = split_strings[1] + split_strings[2]
        main_string = self._tokenize_comments(main_string)
        main_string = self._tokenize_completely_removed(main_string)
        main_string = self._tokenize_specials(main_string)
        main_string = self._tokenize_unnamed_math_optimized(main_string)
        main_string = self._tokenize_commands(main_string)
        main_string = self._tokenize_named_envs(main_string)
        main_string = self._tokenize_markers(main_string)
        main_string = self._tokenize_latex_escapes(main_string)
        self._tokenized_string = header_string + main_string

    def detokenize(self) -> None:
        """Replaces all tokens from a previous tokenization run with their associated original strings.

        First, a regex assisted search and replace is performed to process all tokens with a curly brace syntax. These
        need special handling since the contents of the curly braces need to be first put inside the original string in
        the dictionary and then the whole token-curly brace should be replaced with the modified dictionary value.

        Later, a simple string replace is performed for all the rest of the "normal/simple" tokens.

        Write logs on encounter of any missing or altered tokens in the string to detokenize.

        Raises:
            ValueError: If string to detokenize is empty.

        """
        main_string: str = self._tokenized_string
        if not main_string:
            raise ValueError(
                "Tokenized string is empty, nothing to detokenize"
            )
        for token in self._token_store.keys():
            if main_string.count(token) == 0:
                log.error(
                    "Found missing or altered TOKEN: %s --> during stage TOKENIZER",
                    token,
                )
        pattern = re.compile(
            r"("
            + self._token_regex()
            + r")(?<!\\)(?:\\\\)*\s?((?!"
            + self._token_regex()
            + r")\{(?:[^{}]+|(?2))*\})"
        )
        all_commands_replaced = False
        while not all_commands_replaced:
            match = pattern.search(main_string)
            if match:
                replace_string = self._token_store[match[1]].replace(
                    Tokenizer.DEFAULT_DETOKENIZER_CONTENT_INDICATOR,
                    match[2],
                    1,
                )
                main_string = pattern.sub(replace_string, main_string, 1)
            else:
                all_commands_replaced = True
        for token, value in self._token_store.items():
            main_string = main_string.replace(token, value)
        self._marked_string = main_string
